"""Tests de ui.screens.ScreenManager (chantier ch3)."""

import unittest

from ui.screens import Screen, ScreenManager


class TestScreens(unittest.TestCase):
    def test_initial_state(self) -> None:
        manager = ScreenManager()
        self.assertEqual(manager.current(), Screen.TITLE)
        self.assertEqual(manager.selected_index(), 0)
        self.assertFalse(manager.quit_requested)

    def test_navigation_and_transitions(self) -> None:
        manager = ScreenManager()
        # Navigation vers le bas sur TITLE : index 0 -> 1.
        screen = manager.handle_input(nav=1, validate=False)
        self.assertEqual(screen, Screen.TITLE)
        self.assertEqual(manager.selected_index(), 1)
        # Navigation vers le haut : retour à 0.
        manager.handle_input(nav=-1, validate=False)
        self.assertEqual(manager.selected_index(), 0)
        # Modulo : remonter depuis 0 boucle sur la dernière option.
        manager.handle_input(nav=-1, validate=False)
        self.assertEqual(manager.selected_index(), 2)
        manager.handle_input(nav=1, validate=False)
        self.assertEqual(manager.selected_index(), 0)
        # Validation sur "start" (index 0) -> PLAYING.
        screen = manager.handle_input(nav=0, validate=True)
        self.assertEqual(screen, Screen.PLAYING)
        self.assertEqual(manager.current(), Screen.PLAYING)

    def test_title_options_and_quit(self) -> None:
        manager = ScreenManager()
        manager.handle_input(nav=1, validate=False)  # -> "options"
        screen = manager.handle_input(nav=0, validate=True)
        self.assertEqual(screen, Screen.OPTIONS)
        # Retour au titre via validation sur OPTIONS.
        screen = manager.handle_input(nav=0, validate=True)
        self.assertEqual(screen, Screen.TITLE)
        # Monter jusqu'à "quit" (index 2) puis valider.
        manager.handle_input(nav=1, validate=False)
        manager.handle_input(nav=1, validate=False)
        self.assertEqual(manager.selected_index(), 2)
        screen = manager.handle_input(nav=0, validate=True)
        self.assertEqual(screen, Screen.TITLE)
        self.assertTrue(manager.quit_requested)

    def test_playing_to_game_over(self) -> None:
        manager = ScreenManager()
        manager.handle_input(nav=0, validate=True)  # start -> PLAYING
        self.assertEqual(manager.current(), Screen.PLAYING)
        # Game over détecté -> GAME_OVER.
        screen = manager.handle_input(nav=0, validate=False, game_over=True)
        self.assertEqual(screen, Screen.GAME_OVER)
        self.assertEqual(manager.current(), Screen.GAME_OVER)
        # Validation sur GAME_OVER -> retour au TITLE.
        screen = manager.handle_input(nav=0, validate=True)
        self.assertEqual(screen, Screen.TITLE)

    def test_screen_enum_values(self) -> None:
        self.assertEqual(
            {s.name for s in Screen},
            {"TITLE", "OPTIONS", "PLAYING", "GAME_OVER"},
        )


if __name__ == "__main__":
    unittest.main()
