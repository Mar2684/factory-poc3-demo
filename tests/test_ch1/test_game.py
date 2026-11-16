"""Tests d'intégration du noyau (core.game, core.entities, core.ai)."""

import unittest

from core import (
    AIPlayer,
    Ball,
    Game,
    GameError,
    GamePhase,
    InvalidStateError,
    MatchResult,
    Paddle,
    RulesEngine,
    TableBounds,
)


def make_bounds() -> TableBounds:
    # Filet étroit pour ne pas gêner les services des tests d'intégration.
    return TableBounds(width=800.0, height=600.0, net_width=4.0, net_height=40.0)


class TestEntities(unittest.TestCase):
    def test_ball_update_advances_position(self):
        ball = Ball(x=0.0, y=0.0, vx=10.0, vy=-5.0, radius=8.0)
        ball.update(0.5)
        self.assertAlmostEqual(ball.x, 5.0)
        self.assertAlmostEqual(ball.y, -2.5)

    def test_ball_reset(self):
        ball = Ball(x=1.0, y=2.0, vx=3.0, vy=4.0, radius=8.0)
        ball.reset(100.0, 200.0, -50.0, 25.0)
        self.assertEqual((ball.x, ball.y, ball.vx, ball.vy), (100.0, 200.0, -50.0, 25.0))

    def test_paddle_move_and_clamp(self):
        paddle = Paddle(x=100.0, y=100.0, width=12.0, height=90.0, speed=400.0)
        paddle.move(1, 0.1, 0.0, 600.0)
        self.assertAlmostEqual(paddle.y, 140.0)
        paddle.move(1, 10.0, 0.0, 600.0)  # clamp à max_y - height = 510
        self.assertAlmostEqual(paddle.y, 510.0)
        paddle.move(-1, 10.0, 0.0, 600.0)  # clamp à min_y = 0
        self.assertAlmostEqual(paddle.y, 0.0)
        paddle.move(0, 1.0, 0.0, 600.0)  # direction 0 : pas de mouvement
        self.assertAlmostEqual(paddle.y, 0.0)

    def test_paddle_get_aabb(self):
        paddle = Paddle(x=24.0, y=255.0, width=12.0, height=90.0, speed=420.0)
        self.assertEqual(paddle.get_aabb(), (24.0, 255.0, 12.0, 90.0))


class TestAIPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.bounds = make_bounds()

    def test_invalid_ratio_raises(self):
        for bad in (0.0, -0.5, 1.5):
            with self.subTest(ratio=bad):
                with self.assertRaises(ValueError):
                    AIPlayer(bad)

    def test_compute_direction_toward_predicted_ball(self):
        ai = AIPlayer(max_speed_ratio=0.7)
        right = Paddle(x=764.0, y=300.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=400.0, y=100.0, vx=300.0, vy=0.0, radius=8.0)
        # La balle arrivera en y=100 : la raquette (centrée en 350) doit monter.
        self.assertEqual(ai.compute_direction(ball, right, self.bounds), -1)

    def test_compute_direction_with_wall_bounce(self):
        ai = AIPlayer()
        left = Paddle(x=24.0, y=500.0, width=12.0, height=100.0, speed=420.0)
        # Balle vers la gauche avec vy positif : rebond sur le mur bas prévu.
        ball = Ball(x=400.0, y=550.0, vx=-300.0, vy=200.0, radius=8.0)
        direction = ai.compute_direction(ball, left, self.bounds)
        self.assertIn(direction, (-1, 0, 1))
        # Prédiction : t = (36 - 400) / -300 = 1.2133 ; y brute = 550 + 200*1.2133
        # = 792.7, rebond dans [8, 592] -> y prédit ≈ 391.3. La raquette est
        # centrée en 550 : la balle arrive au-dessus -> elle doit monter (-1).
        self.assertEqual(direction, -1)

    def test_compute_direction_ball_moving_away_goes_to_center(self):
        ai = AIPlayer()
        right = Paddle(x=764.0, y=100.0, width=12.0, height=100.0, speed=420.0)
        ball = Ball(x=400.0, y=300.0, vx=-300.0, vy=0.0, radius=8.0)  # s'éloigne
        # Centre du terrain visé (y=300 -> top=250) : la raquette en y=100 descend.
        self.assertEqual(ai.compute_direction(ball, right, self.bounds), 1)


class TestGame(unittest.TestCase):
    def test_step_updates_ball_position(self):
        """Après le service, step() fait avancer la balle."""
        game = Game(make_bounds(), mode="2p")
        before = game.get_state().ball
        phase = game.step(0.016, {"left": 0, "right": 0})  # service + 1er pas
        after = game.get_state().ball
        self.assertEqual(phase, GamePhase.PLAYING)
        self.assertNotEqual((before.x, before.y), (after.x, after.y))
        # Au pas suivant (sans collision), x avance exactement de vx * dt.
        game.step(0.016, {"left": 0, "right": 0})
        final = game.get_state().ball
        self.assertAlmostEqual(final.x, after.x + after.vx * 0.016)
        self.assertAlmostEqual(final.y, after.y + after.vy * 0.016)

    def test_step_invalid_dt_raises(self):
        game = Game(make_bounds(), mode="2p")
        for bad_dt in (0.0, -0.016):
            with self.subTest(dt=bad_dt):
                with self.assertRaises(InvalidStateError):
                    game.step(bad_dt, {"left": 0, "right": 0})

    def test_invalid_mode_raises(self):
        with self.assertRaises(InvalidStateError):
            Game(make_bounds(), mode="solo")
        self.assertTrue(issubclass(InvalidStateError, GameError))

    def test_invalid_input_raises(self):
        game = Game(make_bounds(), mode="2p")
        with self.assertRaises(InvalidStateError):
            game.step(0.016, {"left": 2, "right": 0})

    def test_get_state_returns_deep_copy(self):
        game = Game(make_bounds(), mode="2p")
        state = game.get_state()
        state.ball.x = 9999.0
        state.score.p1_points = 42
        fresh = game.get_state()
        self.assertNotEqual(fresh.ball.x, 9999.0)
        self.assertNotEqual(fresh.score.p1_points, 42)

    def test_initial_state(self):
        game = Game(make_bounds(), mode="vs_ai")
        state = game.get_state()
        self.assertEqual(state.phase, GamePhase.SERVE)
        self.assertEqual(state.server, 1)
        self.assertEqual(
            (state.score.p1_points, state.score.p2_points, state.score.p1_sets, state.score.p2_sets),
            (0, 0, 0, 0),
        )
        self.assertEqual(state.elapsed, 0.0)

    def test_vs_ai_mode_runs(self):
        game = Game(make_bounds(), mode="vs_ai")
        for _ in range(60):
            phase = game.step(0.016, {"left": 0, "right": 0})
        self.assertIn(phase, (GamePhase.PLAYING, GamePhase.POINT_SCORED))

    def test_training_mode_runs(self):
        game = Game(make_bounds(), mode="training")
        for _ in range(60):
            phase = game.step(0.016, {"left": 0, "right": 0})
        self.assertIn(phase, (GamePhase.PLAYING, GamePhase.POINT_SCORED))

    def test_full_match_to_match_won_and_finish_match(self):
        """Match complet (règles courtes) -> MATCH_WON + MatchResult sérialisable."""
        game = Game(make_bounds(), mode="2p")
        game.rules = RulesEngine(points_per_set=2, sets_to_win=1)
        phase = GamePhase.SERVE
        for _ in range(2000):
            phase = game.step(0.016, {"left": 0, "right": 0})
            if phase == GamePhase.MATCH_WON:
                break
        self.assertEqual(phase, GamePhase.MATCH_WON)
        # step après la fin du match reste sur MATCH_WON.
        self.assertEqual(game.step(0.016, {"left": 0, "right": 0}), GamePhase.MATCH_WON)
        result = game.finish_match()
        self.assertIsInstance(result, MatchResult)
        assert result is not None
        self.assertEqual(result.winner, 2)  # J2 marque sur sortie à droite
        self.assertEqual(result.p2_sets, 1)
        self.assertEqual(result.p1_sets, 0)
        self.assertGreater(result.duration, 0.0)
        # MatchResult est immutable (contrat ch2 : sérialisable).
        with self.assertRaises(AttributeError):
            result.winner = 1  # type: ignore[misc]

    def test_finish_match_none_before_end(self):
        game = Game(make_bounds(), mode="2p")
        game.step(0.016, {"left": 0, "right": 0})
        self.assertIsNone(game.finish_match())

    def test_reset_restarts_match(self):
        game = Game(make_bounds(), mode="2p")
        game.rules = RulesEngine(points_per_set=2, sets_to_win=1)
        for _ in range(2000):
            if game.step(0.016, {"left": 0, "right": 0}) == GamePhase.MATCH_WON:
                break
        self.assertIsNotNone(game.finish_match())
        game.reset()
        state = game.get_state()
        self.assertEqual(state.phase, GamePhase.SERVE)
        self.assertEqual(state.score.p1_sets, 0)
        self.assertEqual(state.score.p2_sets, 0)
        self.assertEqual(state.elapsed, 0.0)
        self.assertIsNone(game.finish_match())


if __name__ == "__main__":
    unittest.main()
