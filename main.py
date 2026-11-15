"""Point d'entrée de l'application : menu principal puis moteur de jeu."""

import tkinter as tk

from config import Config
from game_engine import GameEngine
from game_state import GameMode
from input_handler import InputHandler
from renderer import Renderer

MENU_TITLE = "PING PONG"
MENU_SUBTITLE = "1: Solo vs IA    2: 2 Joueurs    Q: Quitter"
MENU_DELAY_MS = 50


class Application:
    """Fenêtre racine, menu textuel et délégation au GameEngine approprié."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Ping Pong 2D")
        self.config = Config()
        self.renderer = Renderer(self.root, self.config)
        self.input_handler = InputHandler()
        self.input_handler.bind_to_root(self.root)
        self.engine = None
        self.show_menu()

    def show_menu(self) -> None:
        """Affiche le menu principal et attend une saisie clavier via InputHandler."""
        self.renderer.clear()
        self.renderer.draw_message(MENU_TITLE, MENU_SUBTITLE)
        self.renderer.update_display()
        self.root.after(MENU_DELAY_MS, self._menu_loop)

    def _menu_loop(self) -> None:
        """Surveille la dernière touche pressée pour lancer un mode ou quitter."""
        key = self.input_handler.consume_last_key()
        if key == "1":
            self.start_solo()
        elif key == "2":
            self.start_multiplayer()
        elif key in ("q", "Q"):
            self.quit()
        else:
            self.root.after(MENU_DELAY_MS, self._menu_loop)

    def start_solo(self) -> None:
        """Lance une partie solo contre l'IA."""
        self.engine = GameEngine(
            self.root, GameMode.SOLO, self.config, self.renderer, self.input_handler
        )
        self.engine.run()

    def start_multiplayer(self) -> None:
        """Lance une partie à deux joueurs sur clavier partagé."""
        self.engine = GameEngine(
            self.root, GameMode.MULTIPLAYER, self.config, self.renderer, self.input_handler
        )
        self.engine.run()

    def quit(self) -> None:
        """Détruit la fenêtre tkinter et termine le programme."""
        self.root.destroy()


def main() -> None:
    """Instancie l'Application et lance la boucle principale tkinter."""
    app = Application()
    app.root.mainloop()


if __name__ == "__main__":
    main()
