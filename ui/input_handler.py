"""Capture des entrées clavier (chantier ch3).

N'importe que ``tkinter`` : le handler maintient l'état des touches suivies et
le traduit en directions de jeu ou en navigation de menu.
"""

from __future__ import annotations

import tkinter as tk

#: Touches suivies par le handler.
TRACKED_KEYS: tuple[str, ...] = (
    "Up",
    "Down",
    "w",
    "s",
    "space",
    "Return",
    "Escape",
)


class InputHandler:
    """Suit l'état des touches pressées et produit des commandes par tick."""

    def __init__(self) -> None:
        """Initialise ``_pressed`` à False pour chaque touche suivie."""
        self._pressed: dict[str, bool] = {key: False for key in TRACKED_KEYS}

    def bind(self, root: tk.Tk) -> None:
        """Attache les callbacks <KeyPress> et <KeyRelease> sur ``root``.

        Touches suivies : "Up", "Down" (J1), "w", "s" (J2 en mode 2p) ou
        flèches pour J2 en mode vs_ai, "space" (action/serve), "Return"
        (validation menu), "Escape" (quitter).
        """
        root.bind("<KeyPress>", self._on_key_press)
        root.bind("<KeyRelease>", self._on_key_release)

    def poll_game(self) -> dict[str, int]:
        """Retourne {"left": -1|0|1, "right": -1|0|1} selon l'état courant.

        Mapping : Up/w = -1, Down/s = 1 (Up/Down pour J1, w/s pour J2).
        """
        left = -1 if self._pressed["Up"] else (1 if self._pressed["Down"] else 0)
        right = -1 if self._pressed["w"] else (1 if self._pressed["s"] else 0)
        return {"left": left, "right": right}

    def poll_menu(self) -> tuple[int, bool]:
        """Retourne (nav, validate) pour les écrans de menu.

        ``nav`` = -1 si Up pressé, 1 si Down, 0 sinon. ``validate`` = True si
        Return ou space a été pressé ce tick (flag consommé à la lecture).
        """
        nav = -1 if self._pressed["Up"] else (1 if self._pressed["Down"] else 0)
        validate = self._pressed["Return"] or self._pressed["space"]
        if validate:
            self._pressed["Return"] = False
            self._pressed["space"] = False
        return (nav, validate)

    def consume_quit(self) -> bool:
        """Retourne True si Escape a été pressé depuis le dernier appel, puis
        reset le flag."""
        quit_requested = self._pressed["Escape"]
        self._pressed["Escape"] = False
        return quit_requested

    def _on_key_press(self, event: tk.Event) -> None:
        """Callback <KeyPress> : marque la touche comme pressée si suivie."""
        if event.keysym in self._pressed:
            self._pressed[event.keysym] = True

    def _on_key_release(self, event: tk.Event) -> None:
        """Callback <KeyRelease> : marque la touche comme relâchée si suivie."""
        if event.keysym in self._pressed:
            self._pressed[event.keysym] = False
