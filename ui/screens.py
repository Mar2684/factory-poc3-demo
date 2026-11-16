"""Gestion des écrans du jeu (chantier ch3) : titre, options, jeu, fin.

N'importe que ``enum`` : la logique de navigation est pure et testable sans
tkinter.
"""

from __future__ import annotations

from enum import Enum


class Screen(Enum):
    """Écrans possibles de l'application."""

    TITLE = "title"
    OPTIONS = "options"
    PLAYING = "playing"
    GAME_OVER = "game_over"


#: Options du menu titre (dans l'ordre, l'index 0 = "start" par défaut).
TITLE_OPTIONS: tuple[str, ...] = ("start", "options", "quit")
#: Options de l'écran des paramètres.
OPTIONS_OPTIONS: tuple[str, ...] = ("back",)


class ScreenManager:
    """État de navigation entre les écrans et index du menu sélectionné."""

    def __init__(self) -> None:
        """État initial : écran TITLE, selected_index = 0."""
        self._current: Screen = Screen.TITLE
        self._selected_index: int = 0
        #: Mis à True quand l'utilisateur choisit "quit" sur le menu titre.
        self.quit_requested: bool = False

    def current(self) -> Screen:
        """Retourne l'écran actif."""
        return self._current

    def selected_index(self) -> int:
        """Retourne l'index du menu sélectionné."""
        return self._selected_index

    def handle_input(self, nav: int, validate: bool, game_over: bool = False) -> Screen:
        """Met à jour l'écran courant selon la navigation et la validation.

        - TITLE/OPTIONS : ``nav`` ≠ 0 incrémente/décrémente ``selected_index``
          (modulo le nombre d'options) ; ``validate`` sur TITLE déclenche
          "start" -> PLAYING, "options" -> OPTIONS, "quit" -> signale quit via
          ``quit_requested`` en restant sur TITLE ; ``validate`` sur OPTIONS
          retourne à TITLE.
        - PLAYING : si ``game_over`` détecté -> GAME_OVER.
        - GAME_OVER : ``validate`` retourne à TITLE (nouvelle partie).

        Retourne le nouvel écran actif.
        """
        if self._current in (Screen.TITLE, Screen.OPTIONS):
            options = self._options_for(self._current)
            if nav != 0 and options:
                self._selected_index = (self._selected_index + nav) % len(options)
            if validate:
                self._validate_menu()
        elif self._current == Screen.PLAYING:
            if game_over:
                self._current = Screen.GAME_OVER
        elif self._current == Screen.GAME_OVER:
            if validate:
                self._current = Screen.TITLE
                self._selected_index = 0
        return self._current

    def _options_for(self, screen: Screen) -> tuple[str, ...]:
        """Retourne les options du menu pour l'écran donné."""
        if screen == Screen.TITLE:
            return TITLE_OPTIONS
        if screen == Screen.OPTIONS:
            return OPTIONS_OPTIONS
        return ()

    def _validate_menu(self) -> None:
        """Applique la validation sur l'écran TITLE ou OPTIONS."""
        if self._current == Screen.TITLE:
            choice = TITLE_OPTIONS[self._selected_index]
            if choice == "start":
                self._current = Screen.PLAYING
                self._selected_index = 0
            elif choice == "options":
                self._current = Screen.OPTIONS
                self._selected_index = 0
            elif choice == "quit":
                self.quit_requested = True
        elif self._current == Screen.OPTIONS:
            self._current = Screen.TITLE
            self._selected_index = 0
