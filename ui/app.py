"""Application tkinter : boucle principale à 60 FPS et gestion des écrans
(chantier ch3).

Importe ``core.game`` (Game), ``meta.storage`` (ScoreStorage),
``meta.models`` (GameSettings) et les modules ``ui.renderer``,
``ui.input_handler``, ``ui.screens``.
"""

from __future__ import annotations

import time
import tkinter as tk

from core.game import Game, MatchResult
from meta.models import GameSettings
from meta.storage import ScoreStorage
from ui.input_handler import InputHandler
from ui.renderer import Renderer
from ui.screens import TITLE_OPTIONS, Screen, ScreenManager

#: Période d'un tick de la boucle principale (~60 FPS).
TICK_MS: int = 16
#: ``dt`` maximal appliqué à la simulation (évite les sauts après une pause).
MAX_DT_SECONDS: float = 0.05


class PingPongApp:
    """Fenêtre principale, boucle de jeu à 60 FPS et navigation des écrans."""

    def __init__(self, game: Game, storage: ScoreStorage, settings: GameSettings) -> None:
        """Crée la fenêtre, le canvas, le Renderer, l'InputHandler et le
        ScreenManager."""
        self.game = game
        self.storage = storage
        self.settings = settings
        self.root = tk.Tk()
        self.canvas = tk.Canvas(
            self.root,
            width=settings.window_width,
            height=settings.window_height,
            bg="#0b3d20",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.renderer = Renderer(self.canvas, scale=1.0, margin=20)
        self.renderer.set_bounds(game.bounds)
        self.input_handler = InputHandler()
        self.screen_manager = ScreenManager()
        self._last_time: float = time.perf_counter()
        self._last_result: MatchResult | None = None
        self._running: bool = False

    def run(self) -> None:
        """Configure la fenêtre, bind les entrées, lance la boucle à 60 FPS
        via ``root.after(16, self._tick)`` puis ``root.mainloop()``."""
        self.root.title("Ping Pong 2D")
        self.root.geometry(
            f"{self.settings.window_width}x{self.settings.window_height}"
        )
        self.input_handler.bind(self.root)
        self._running = True
        self._last_time = time.perf_counter()
        self.root.after(TICK_MS, self._tick)
        self.root.mainloop()

    def _tick(self) -> None:
        """Un pas de boucle (~16 ms) : calcule le dt réel, met à jour l'écran
        actif et programme le tick suivant."""
        now = time.perf_counter()
        dt = min(now - self._last_time, MAX_DT_SECONDS)
        self._last_time = now
        if dt <= 0.0:
            dt = TICK_MS / 1000.0

        if self.input_handler.consume_quit():
            self._shutdown()
            return

        screen = self.screen_manager.current()
        if screen == Screen.PLAYING:
            self._tick_playing(dt)
        elif screen == Screen.TITLE:
            self._tick_title()
            if self.screen_manager.quit_requested:
                self._shutdown()
                return
        elif screen == Screen.OPTIONS:
            self._tick_options()
        elif screen == Screen.GAME_OVER:
            self._tick_game_over()

        self.root.after(TICK_MS, self._tick)

    def _tick_playing(self, dt: float) -> None:
        """Un pas de jeu : entrées -> directions (sensibilité) -> step -> rendu."""
        raw_inputs = self.input_handler.poll_game()
        sensitivity = self.settings.paddle_sensitivity
        inputs: dict[str, int] = {}
        for side, direction in raw_inputs.items():
            value = direction * sensitivity
            # Le contrat de Game.step exige des directions dans {-1, 0, 1} :
            # la sensibilité (positive) ne change que l'amplitude, on clamp.
            inputs[side] = 1 if value > 0 else (-1 if value < 0 else 0)
        self.game.step(dt, inputs)
        result = self.game.finish_match()
        if result is not None:
            self._last_result = result
            self.storage.add_result(result)
            self.screen_manager.handle_input(0, False, game_over=True)
        else:
            self.renderer.draw_game(self.game.get_state())

    def _tick_title(self) -> None:
        """Écran titre : navigation menu puis rendu du menu."""
        nav, validate = self.input_handler.poll_menu()
        self.screen_manager.handle_input(nav, validate)
        self.renderer.draw_title(
            self.screen_manager.selected_index(), list(TITLE_OPTIONS)
        )

    def _tick_options(self) -> None:
        """Écran options : navigation (retour) puis rendu des paramètres."""
        nav, validate = self.input_handler.poll_menu()
        self.screen_manager.handle_input(nav, validate)
        self.renderer.draw_options(self.settings)

    def _tick_game_over(self) -> None:
        """Écran de fin : validation -> nouvelle partie, puis rendu du résultat."""
        nav, validate = self.input_handler.poll_menu()
        if validate:
            self.game.reset()
            self._last_result = None
        self.screen_manager.handle_input(nav, validate)
        if self._last_result is not None:
            self.renderer.draw_game_over(self._last_result)

    def _shutdown(self) -> None:
        """Quitte proprement l'application (Escape ou "quit" du menu)."""
        self._running = False
        self.root.destroy()
