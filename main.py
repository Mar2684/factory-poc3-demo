"""Point d'entrée du jeu Ping Pong 2D (chantier ch3).

Construit le noyau (``core``), la persistance (``meta``) et lance
l'application Tkinter (``ui``).
"""

from pathlib import Path

from core.entities import TableBounds
from core.game import Game
from meta.models import GameSettings
from meta.storage import ScoreStorage
from ui.app import PingPongApp


def main() -> None:
    """Construit les dépendances et lance la boucle principale."""
    bounds = TableBounds(width=800.0, height=600.0, net_width=4.0, net_height=600.0)
    game = Game(bounds, mode="vs_ai")
    storage = ScoreStorage(Path.home() / ".pingpong")
    settings: GameSettings = storage.load_settings()
    app = PingPongApp(game, storage, settings)
    app.run()


if __name__ == "__main__":
    main()
