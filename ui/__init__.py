"""Package ui (chantier ch3) : interface graphique Tkinter, boucle de jeu
60 FPS et gestion des écrans.

Réexporte les symboles publics : ``PingPongApp``, ``Renderer``,
``InputHandler``, ``ScreenManager``, ``Screen``.
"""

from ui.app import PingPongApp
from ui.input_handler import InputHandler
from ui.renderer import Renderer
from ui.screens import Screen, ScreenManager

__all__ = [
    "PingPongApp",
    "Renderer",
    "InputHandler",
    "ScreenManager",
    "Screen",
]
