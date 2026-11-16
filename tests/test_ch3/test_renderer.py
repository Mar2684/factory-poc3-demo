"""Tests de ui.renderer.Renderer avec un canvas mocké (chantier ch3)."""

import unittest
from unittest.mock import MagicMock

from core.entities import Ball, Paddle, TableBounds
from core.game import GameState, MatchResult
from core.rules import GamePhase, Score
from meta.models import GameSettings
from ui.renderer import Renderer


def make_state() -> GameState:
    """Construit un GameState fictif pour le rendu."""
    return GameState(
        ball=Ball(x=400.0, y=300.0, vx=120.0, vy=-40.0, radius=8.0),
        left_paddle=Paddle(x=24.0, y=250.0, width=12.0, height=90.0, speed=420.0),
        right_paddle=Paddle(x=764.0, y=260.0, width=12.0, height=90.0, speed=420.0),
        score=Score(p1_points=3, p2_points=2, p1_sets=1, p2_sets=0),
        phase=GamePhase.PLAYING,
        server=1,
        elapsed=12.5,
    )


class TestRenderer(unittest.TestCase):
    def setUp(self) -> None:
        self.canvas = MagicMock()
        self.renderer = Renderer(self.canvas, scale=1.0, margin=20)
        self.renderer.set_bounds(
            TableBounds(width=800.0, height=600.0, net_width=4.0, net_height=600.0)
        )

    def test_clear_deletes_all(self) -> None:
        self.renderer.clear()
        self.canvas.delete.assert_called_once_with("all")

    def test_draw_game_invokes_canvas(self) -> None:
        self.renderer.draw_game(make_state())
        # clear() appelé en début de draw_game.
        self.canvas.delete.assert_called_with("all")
        # Balle = ovale (au moins une fois).
        self.assertGreaterEqual(self.canvas.create_oval.call_count, 1)
        # Raquettes = rectangles (au moins 2, plus le fond).
        self.assertGreaterEqual(self.canvas.create_rectangle.call_count, 2)
        # Filet = ligne verticale centrée (x = margin + width/2 = 420).
        self.assertGreaterEqual(self.canvas.create_line.call_count, 1)
        net_call = self.canvas.create_line.call_args_list[0]
        self.assertEqual(net_call.args[0], 420.0)
        self.assertEqual(net_call.args[2], 420.0)
        # Score affiché en haut.
        texts = [
            call.kwargs.get("text", "") for call in self.canvas.create_text.call_args_list
        ]
        self.assertTrue(any("P1: 3 - 2 :P2" in text for text in texts))

    def test_draw_game_ball_oval_centered_on_ball(self) -> None:
        self.renderer.draw_game(make_state())
        oval_call = self.canvas.create_oval.call_args_list[0]
        # Balle (400, 300), rayon 8, margin 20, scale 1 -> ovale centré en (420, 320).
        self.assertEqual(oval_call.args, (412.0, 312.0, 428.0, 328.0))

    def test_draw_title_highlights_selected_option(self) -> None:
        options = ["start", "options", "quit"]
        self.renderer.draw_title(1, options)
        text_calls = self.canvas.create_text.call_args_list
        # Titre + 3 options.
        self.assertEqual(len(text_calls), 4)
        self.assertIn("PING PONG 2D", text_calls[0].kwargs["text"])
        # L'option sélectionnée (index 1) a la couleur de surlignage.
        self.assertEqual(text_calls[2].kwargs["text"], "options")
        self.assertNotEqual(
            text_calls[2].kwargs["fill"], text_calls[1].kwargs["fill"]
        )

    def test_draw_game_over_shows_winner_and_sets(self) -> None:
        result = MatchResult(p1_sets=3, p2_sets=1, winner=1, duration=42.0)
        self.renderer.draw_game_over(result)
        texts = [
            call.kwargs.get("text", "") for call in self.canvas.create_text.call_args_list
        ]
        self.assertTrue(any("Player 1 Wins!" in text for text in texts))
        self.assertTrue(any("3 - 1" in text for text in texts))

    def test_draw_options_shows_settings(self) -> None:
        settings = GameSettings(
            paddle_sensitivity=1.5, volume=0.4, window_width=1024, window_height=768
        )
        self.renderer.draw_options(settings)
        texts = [
            call.kwargs.get("text", "") for call in self.canvas.create_text.call_args_list
        ]
        self.assertTrue(any("Volume: 0.40" in text for text in texts))
        self.assertTrue(any("sensitivity: 1.50" in text for text in texts))
        self.assertTrue(any("1024 x 768" in text for text in texts))


if __name__ == "__main__":
    unittest.main()
