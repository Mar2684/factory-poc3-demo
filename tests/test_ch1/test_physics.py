"""Tests du moteur physique (core.physics) — rebonds raquettes, murs, filet."""

import unittest

from core.entities import Ball, Paddle, TableBounds
from core.physics import CollisionType, PhysicsEngine


def make_bounds() -> TableBounds:
    return TableBounds(width=800.0, height=600.0, net_width=6.0, net_height=200.0)


class TestPhysics(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PhysicsEngine()
        self.bounds = make_bounds()

    def test_paddle_bounce_inverts_vx(self):
        """Balle vers la gauche + raquette gauche devant -> vx > 0, LEFT_PADDLE."""
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=30.0, y=300.0, vx=-200.0, vy=0.0, radius=8.0)
        collision = self.engine.resolve(ball, left, right, self.bounds)
        self.assertEqual(collision, CollisionType.LEFT_PADDLE)
        self.assertGreater(ball.vx, 0.0)

    def test_right_paddle_bounce_inverts_vx(self):
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=758.0, y=300.0, vx=250.0, vy=0.0, radius=8.0)
        collision = self.engine.resolve(ball, left, right, self.bounds)
        self.assertEqual(collision, CollisionType.RIGHT_PADDLE)
        self.assertLess(ball.vx, 0.0)

    def test_bounce_angle_depends_on_impact_position(self):
        """Impact au-dessus du centre -> vy < 0 ; angle max 60° au bord."""
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        # Impact en haut de la raquette (y=255, centre=300) -> vy négatif.
        ball = Ball(x=30.0, y=255.0, vx=-200.0, vy=0.0, radius=8.0)
        self.engine.resolve(ball, left, right, self.bounds)
        self.assertGreater(ball.vx, 0.0)
        self.assertLess(ball.vy, 0.0)
        # Impact au bord extrême -> angle <= 60° par rapport à l'horizontale.
        ball2 = Ball(x=30.0, y=250.0, vx=-200.0, vy=0.0, radius=8.0)
        self.engine.resolve(ball2, left, right, self.bounds)
        import math

        angle = math.degrees(math.atan2(abs(ball2.vy), abs(ball2.vx)))
        self.assertLessEqual(angle, 60.0 + 1e-9)

    def test_top_wall_bounce_inverts_vy(self):
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=400.0, y=5.0, vx=0.0, vy=-100.0, radius=8.0)
        collision = self.engine.resolve(ball, left, right, self.bounds)
        self.assertEqual(collision, CollisionType.TOP_WALL)
        self.assertGreater(ball.vy, 0.0)

    def test_bottom_wall_bounce_inverts_vy(self):
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=400.0, y=597.0, vx=0.0, vy=100.0, radius=8.0)
        collision = self.engine.resolve(ball, left, right, self.bounds)
        self.assertEqual(collision, CollisionType.BOTTOM_WALL)
        self.assertLess(ball.vy, 0.0)

    def test_net_bounce_inverts_vx(self):
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        # Filet centré : x ∈ [397, 403], y ∈ [200, 400].
        ball = Ball(x=395.0, y=300.0, vx=100.0, vy=0.0, radius=8.0)
        collision = self.engine.resolve(ball, left, right, self.bounds)
        self.assertEqual(collision, CollisionType.NET)
        self.assertLess(ball.vx, 0.0)

    def test_no_collision_returns_none(self):
        left = Paddle(x=24.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        right = Paddle(x=764.0, y=250.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=500.0, y=100.0, vx=50.0, vy=20.0, radius=8.0)
        collision = self.engine.resolve(ball, left, right, self.bounds)
        self.assertEqual(collision, CollisionType.NONE)
        self.assertEqual((ball.vx, ball.vy), (50.0, 20.0))


if __name__ == "__main__":
    unittest.main()
