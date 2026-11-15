"""Suite de tests unitaires du jeu de ping-pong 2D (stdlib uniquement)."""

import math
import unittest
from unittest.mock import MagicMock

from ai_controller import AIController
from config import Config
from entities import Ball, Paddle
from game_engine import GameEngine
from game_state import GameMode, GameStatus, Score
from input_handler import InputHandler


class TestBallPhysics(unittest.TestCase):
    def test_wall_bounce_inverts_vertical_velocity(self):
        ball = Ball(400.0, 10.0, 8, 5.0, -3.0, "#ffffff")
        ball.reverse_y()
        speed_x, speed_y = ball.get_velocity()
        self.assertEqual(speed_x, 5.0)
        self.assertGreater(speed_y, 0)

    def test_paddle_collision_reverses_horizontal_direction(self):
        paddle = Paddle(20, 250, 15, 90, 7, "#ffffff")
        ball = Ball(40.0, 295.0, 8, -5.0, 0.0, "#ffffff")
        self.assertTrue(paddle.collides_with(ball.x, ball.y, ball.radius))
        ball.bounce_off_paddle(paddle, 600)
        speed_x, _speed_y = ball.get_velocity()
        self.assertGreater(speed_x, 0)  # le signe de speed_x a changé
        # la balle ne pénètre pas dans la raquette après l'appel
        ball_x, ball_y = ball.get_position()
        closest_x = max(paddle.x, min(ball_x, paddle.x + paddle.width))
        closest_y = max(paddle.y, min(ball_y, paddle.y + paddle.height))
        distance = math.hypot(ball_x - closest_x, ball_y - closest_y)
        self.assertGreaterEqual(distance, ball.radius)

    def test_increase_speed_scales_both_components(self):
        ball = Ball(0.0, 0.0, 8, 4.0, -2.0, "#ffffff")
        ball.increase_speed(1.5)
        self.assertAlmostEqual(ball.get_velocity()[0], 6.0)
        self.assertAlmostEqual(ball.get_velocity()[1], -3.0)


class TestScoreLogic(unittest.TestCase):
    def test_game_over_at_winning_score(self):
        score = Score()
        for _ in range(5):
            score.increment_player1()
        self.assertTrue(score.is_game_over(5))
        self.assertEqual(score.get_winner(5), 1)
        self.assertEqual(score.get_scores(), (5, 0))

    def test_not_game_over_below_winning_score(self):
        score = Score()
        score.increment_player2()
        score.increment_player2()
        self.assertFalse(score.is_game_over(5))
        self.assertIsNone(score.get_winner(5))
        score.reset()
        self.assertEqual(score.get_scores(), (0, 0))


class TestPaddleMovement(unittest.TestCase):
    def test_paddle_respects_screen_bounds(self):
        paddle = Paddle(20, 0, 15, 90, 7, "#ffffff")
        for _ in range(10):
            paddle.move_up(600)
        self.assertEqual(paddle.get_bounds()[1], 0)
        paddle.set_y(590, 600)
        for _ in range(20):
            paddle.move_down(600)
        _x, y, _w, height = paddle.get_bounds()
        self.assertLessEqual(y + height, 600)
        self.assertEqual(y, 600 - 90)

    def test_set_y_clamps_to_bounds(self):
        paddle = Paddle(20, 100, 15, 90, 7, "#ffffff")
        paddle.set_y(-50, 600)
        self.assertEqual(paddle.get_bounds()[1], 0)
        paddle.set_y(10000, 600)
        self.assertEqual(paddle.get_bounds()[1], 600 - 90)


class TestAIController(unittest.TestCase):
    def test_ai_moves_toward_ball(self):
        paddle = Paddle(765, 300, 15, 90, 7, "#ffffff")
        ball = Ball(400.0, 50.0, 8, -5.0, 0.0, "#ffffff")
        ai = AIController(paddle, difficulty=1.0)
        ai.update(ball, 600)
        self.assertLess(paddle.get_bounds()[1], 300)  # la raquette est montée vers la balle

    def test_ai_respects_screen_bounds(self):
        paddle = Paddle(765, 0, 15, 90, 7, "#ffffff")
        ball = Ball(400.0, 5.0, 8, -5.0, 0.0, "#ffffff")
        ai = AIController(paddle, difficulty=1.0)
        for _ in range(20):
            ai.update(ball, 600)
        self.assertGreaterEqual(paddle.get_bounds()[1], 0)


class TestInputHandler(unittest.TestCase):
    def test_player_directions(self):
        handler = InputHandler()
        self.assertEqual(handler.get_player1_direction(), 0)
        handler.handle_key_press("z")
        self.assertEqual(handler.get_player1_direction(), -1)
        handler.handle_key_release("z")
        handler.handle_key_press("s")
        self.assertEqual(handler.get_player1_direction(), 1)
        handler.handle_key_release("s")
        handler.handle_key_press("Up")
        self.assertEqual(handler.get_player2_direction(), -1)
        handler.handle_key_release("Up")
        handler.handle_key_press("Down")
        self.assertEqual(handler.get_player2_direction(), 1)

    def test_consume_pause_request(self):
        handler = InputHandler()
        self.assertFalse(handler.consume_pause_request())
        handler.handle_key_press("p")
        self.assertTrue(handler.consume_pause_request())
        self.assertFalse(handler.consume_pause_request())
        handler.handle_key_press("space")
        self.assertTrue(handler.consume_pause_request())


class TestGameEngineScoring(unittest.TestCase):
    def _make_engine(self, mode=GameMode.MULTIPLAYER):
        config = Config()
        root = MagicMock()
        renderer = MagicMock()
        input_handler = MagicMock()
        input_handler.get_player1_direction.return_value = 0
        input_handler.get_player2_direction.return_value = 0
        input_handler.consume_pause_request.return_value = False
        engine = GameEngine(root, mode, config, renderer, input_handler)
        return engine, config

    def test_ball_exit_right_increments_player1(self):
        engine, config = self._make_engine()
        engine.ball.reset(config.screen_width - 2, 300.0, config.ball_speed_x, 0.0)
        engine.update()
        self.assertEqual(engine.score.get_scores(), (1, 0))
        ball_x, ball_y = engine.ball.get_position()
        self.assertEqual(ball_x, config.screen_width / 2.0)
        self.assertEqual(ball_y, config.screen_height / 2.0)

    def test_ball_exit_left_increments_player2(self):
        engine, config = self._make_engine()
        engine.ball.reset(2.0, 300.0, -config.ball_speed_x, 0.0)
        engine.update()
        self.assertEqual(engine.score.get_scores(), (0, 1))

    def test_check_scoring_returns_scorer(self):
        engine, config = self._make_engine()
        engine.ball.reset(config.screen_width + 1, 300.0, config.ball_speed_x, 0.0)
        self.assertEqual(engine.check_scoring(), 1)
        engine.ball.reset(-1.0, 300.0, -config.ball_speed_x, 0.0)
        self.assertEqual(engine.check_scoring(), 2)
        engine.ball.reset(400.0, 300.0, 0.0, 0.0)
        self.assertEqual(engine.check_scoring(), 0)

    def test_wall_bounce_keeps_ball_in_vertical_bounds(self):
        engine, config = self._make_engine()
        engine.ball.reset(400.0, 5.0, 0.0, -5.0)
        engine.update()
        _speed_x, speed_y = engine.ball.get_velocity()
        self.assertGreater(speed_y, 0)
        self.assertGreaterEqual(engine.ball.get_position()[1], engine.ball.radius)

    def test_toggle_pause(self):
        engine, _config = self._make_engine()
        self.assertEqual(engine.status, GameStatus.PLAYING)
        engine.toggle_pause()
        self.assertEqual(engine.status, GameStatus.PAUSED)
        engine.toggle_pause()
        self.assertEqual(engine.status, GameStatus.PLAYING)

    def test_game_over_and_winner(self):
        engine, config = self._make_engine()
        for _ in range(config.winning_score):
            engine.score.increment_player2()
        engine.update()
        self.assertTrue(engine.is_game_over())
        self.assertEqual(engine.status, GameStatus.GAME_OVER)
        self.assertEqual(engine.get_winner(), 2)

    def test_solo_mode_creates_ai_controller(self):
        engine, _config = self._make_engine(mode=GameMode.SOLO)
        self.assertIsNotNone(engine.ai_controller)
        multiplayer_engine, _ = self._make_engine(mode=GameMode.MULTIPLAYER)
        self.assertIsNone(multiplayer_engine.ai_controller)


if __name__ == "__main__":
    unittest.main()
