"""Moteur physique : détection et résolution des collisions (rebonds).

Importe uniquement ``core.entities`` : aucune dépendance graphique.
"""

import math
from enum import Enum

from core.entities import Ball, Paddle, TableBounds

#: Angle maximal de rebond sur une raquette (par rapport à l'horizontale).
MAX_BOUNCE_ANGLE_DEG: float = 60.0


class CollisionType(Enum):
    """Type de collision détectée lors d'un pas de simulation."""

    NONE = "none"
    LEFT_PADDLE = "left_paddle"
    RIGHT_PADDLE = "right_paddle"
    NET = "net"
    TOP_WALL = "top_wall"
    BOTTOM_WALL = "bottom_wall"


def _circle_intersects_rect(
    ball: Ball, rx: float, ry: float, rw: float, rh: float
) -> bool:
    """Vrai si le cercle de la balle intersecte le rectangle (rx, ry, rw, rh)."""
    closest_x = max(rx, min(ball.x, rx + rw))
    closest_y = max(ry, min(ball.y, ry + rh))
    dx = ball.x - closest_x
    dy = ball.y - closest_y
    return dx * dx + dy * dy <= ball.radius * ball.radius


class PhysicsEngine:
    """Détecte et applique les rebonds (modifie ``ball.vx`` / ``ball.vy``)."""

    def resolve(
        self,
        ball: Ball,
        left: Paddle,
        right: Paddle,
        bounds: TableBounds,
    ) -> CollisionType:
        """Détecte la première collision et applique le rebond correspondant.

        - Raquettes : inversion de ``vx`` et ajustement de ``vy`` selon la
          position d'impact relative au centre de la raquette (angle max 60°).
        - Filet (rectangle centré sur le terrain) : inversion de ``vx``.
        - Murs haut/bas : inversion de ``vy``.

        Retourne le type de collision détectée.
        """
        # Raquette gauche : seulement si la balle se dirige vers elle.
        if ball.vx < 0 and _circle_intersects_rect(ball, *left.get_aabb()):
            self._bounce_off_paddle(ball, left, direction=+1)
            return CollisionType.LEFT_PADDLE
        # Raquette droite.
        if ball.vx > 0 and _circle_intersects_rect(ball, *right.get_aabb()):
            self._bounce_off_paddle(ball, right, direction=-1)
            return CollisionType.RIGHT_PADDLE
        # Filet : rectangle centré au milieu du terrain.
        net_x = bounds.width / 2.0 - bounds.net_width / 2.0
        net_y = bounds.height / 2.0 - bounds.net_height / 2.0
        if _circle_intersects_rect(ball, net_x, net_y, bounds.net_width, bounds.net_height):
            ball.vx = -ball.vx
            return CollisionType.NET
        # Murs haut / bas.
        if ball.vy < 0 and ball.y - ball.radius <= 0.0:
            ball.y = ball.radius
            ball.vy = -ball.vy
            return CollisionType.TOP_WALL
        if ball.vy > 0 and ball.y + ball.radius >= bounds.height:
            ball.y = bounds.height - ball.radius
            ball.vy = -ball.vy
            return CollisionType.BOTTOM_WALL
        return CollisionType.NONE

    def _bounce_off_paddle(self, ball: Ball, paddle: Paddle, direction: int) -> None:
        """Rebond sur raquette : vx inversé, vy ajusté (angle max 60°).

        ``direction`` vaut +1 pour la raquette gauche (balle repart à
        droite) et -1 pour la raquette droite.
        """
        paddle_center_y = paddle.y + paddle.height / 2.0
        half_height = paddle.height / 2.0
        if half_height <= 0.0:
            relative = 0.0
        else:
            relative = (ball.y - paddle_center_y) / half_height
        relative = max(-1.0, min(1.0, relative))
        angle = relative * math.radians(MAX_BOUNCE_ANGLE_DEG)
        speed = math.hypot(ball.vx, ball.vy)
        ball.vx = direction * speed * math.cos(angle)
        ball.vy = speed * math.sin(angle)
        # Repositionne la balle juste devant la raquette (pas de pénétration).
        if direction > 0:
            ball.x = paddle.x + paddle.width + ball.radius
        else:
            ball.x = paddle.x - ball.radius
