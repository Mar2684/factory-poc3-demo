"""Tests de ui.input_handler.InputHandler (chantier ch3)."""

import unittest

from ui.input_handler import InputHandler


class TestInput(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = InputHandler()

    def test_initial_state_all_released(self) -> None:
        self.assertFalse(any(self.handler._pressed.values()))
        self.assertEqual(self.handler.poll_game(), {"left": 0, "right": 0})

    def test_poll_game_mapping(self) -> None:
        # Up -> left = -1
        self.handler._pressed["Up"] = True
        result = self.handler.poll_game()
        self.assertEqual(result["left"], -1)
        self.assertEqual(result["right"], 0)
        # Down -> left = 1
        self.handler._pressed["Up"] = False
        self.handler._pressed["Down"] = True
        result = self.handler.poll_game()
        self.assertEqual(result["left"], 1)
        # w -> right = -1, s -> right = 1
        self.handler._pressed["Down"] = False
        self.handler._pressed["w"] = True
        self.assertEqual(self.handler.poll_game()["right"], -1)
        self.handler._pressed["w"] = False
        self.handler._pressed["s"] = True
        self.assertEqual(self.handler.poll_game()["right"], 1)
        self.assertEqual(self.handler.poll_game()["left"], 0)

    def test_poll_menu_nav_and_validate(self) -> None:
        nav, validate = self.handler.poll_menu()
        self.assertEqual(nav, 0)
        self.assertFalse(validate)
        self.handler._pressed["Down"] = True
        self.handler._pressed["Return"] = True
        nav, validate = self.handler.poll_menu()
        self.assertEqual(nav, 1)
        self.assertTrue(validate)
        # validate est consommé : plus de validation au tick suivant.
        nav, validate = self.handler.poll_menu()
        self.assertEqual(nav, 1)  # Down encore pressé
        self.assertFalse(validate)
        # space fonctionne aussi comme validation.
        self.handler._pressed["space"] = True
        _, validate = self.handler.poll_menu()
        self.assertTrue(validate)

    def test_consume_quit(self) -> None:
        self.assertFalse(self.handler.consume_quit())
        self.handler._pressed["Escape"] = True
        self.assertTrue(self.handler.consume_quit())
        # flag resetté après consommation.
        self.assertFalse(self.handler.consume_quit())

    def test_key_callbacks_update_tracked_keys(self) -> None:
        class FakeEvent:
            def __init__(self, keysym: str) -> None:
                self.keysym = keysym

        self.handler._on_key_press(FakeEvent("Up"))  # type: ignore[arg-type]
        self.assertTrue(self.handler._pressed["Up"])
        self.handler._on_key_release(FakeEvent("Up"))  # type: ignore[arg-type]
        self.assertFalse(self.handler._pressed["Up"])
        # Touche non suivie : ignorée, pas d'erreur.
        self.handler._on_key_press(FakeEvent("x"))  # type: ignore[arg-type]
        self.assertNotIn("x", self.handler._pressed)


if __name__ == "__main__":
    unittest.main()
