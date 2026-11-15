"""Gestion des entrées clavier (état des touches en temps réel)."""

from typing import Optional, Set

import tkinter as tk


class InputHandler:
    """Capture l'état des touches et fournit des directions discrètes (-1, 0, +1)."""

    PAUSE_KEYS = ("p", "space")

    def __init__(self) -> None:
        self.pressed_keys: Set[str] = set()
        self.pause_requested: bool = False
        self._last_key: Optional[str] = None

    def bind_to_root(self, root: tk.Tk) -> None:
        """Attache les callbacks clavier de la fenêtre tkinter aux méthodes internes."""
        root.bind("<KeyPress>", lambda event: self.handle_key_press(event.keysym))
        root.bind("<KeyRelease>", lambda event: self.handle_key_release(event.keysym))

    def handle_key_press(self, key: str) -> None:
        """Enregistre qu'une touche est enfoncée (binding tkinter ou appel direct en test)."""
        self.pressed_keys.add(key)
        self._last_key = key
        if key in self.PAUSE_KEYS:
            self.pause_requested = True

    def handle_key_release(self, key: str) -> None:
        """Enregistre qu'une touche est relâchée."""
        self.pressed_keys.discard(key)

    def get_player1_direction(self) -> int:
        """Retourne -1 si 'z' est enfoncé, +1 si 's' est enfoncé, 0 sinon."""
        if "z" in self.pressed_keys:
            return -1
        if "s" in self.pressed_keys:
            return 1
        return 0

    def get_player2_direction(self) -> int:
        """Retourne -1 si 'Up' est enfoncé, +1 si 'Down' est enfoncé, 0 sinon (mode multijoueur)."""
        if "Up" in self.pressed_keys:
            return -1
        if "Down" in self.pressed_keys:
            return 1
        return 0

    def consume_pause_request(self) -> bool:
        """Retourne True si une touche de pause a été pressée depuis le dernier appel, puis réinitialise."""
        if self.pause_requested:
            self.pause_requested = False
            return True
        return False

    def consume_last_key(self) -> Optional[str]:
        """Retourne la dernière touche pressée depuis le dernier appel, puis réinitialise."""
        key = self._last_key
        self._last_key = None
        return key

    def is_key_pressed(self, key: str) -> bool:
        """Retourne True si la touche est actuellement enfoncée."""
        return key in self.pressed_keys
