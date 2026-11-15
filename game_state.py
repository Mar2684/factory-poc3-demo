"""État du jeu : modes, statuts et score."""

from enum import Enum
from typing import Optional, Tuple


class GameMode(Enum):
    """Mode de jeu disponible."""

    SOLO = "solo"
    MULTIPLAYER = "multiplayer"


class GameStatus(Enum):
    """Statut courant de la partie."""

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class Score:
    """Score des deux joueurs (joueur 1 = gauche, joueur 2 = droite)."""

    def __init__(self) -> None:
        self.player1 = 0
        self.player2 = 0

    def increment_player1(self) -> None:
        """Incrémente le score du joueur 1 (côté gauche)."""
        self.player1 += 1

    def increment_player2(self) -> None:
        """Incrémente le score du joueur 2 (côté droit)."""
        self.player2 += 1

    def get_scores(self) -> Tuple[int, int]:
        """Retourne le couple (score_joueur1, score_joueur2)."""
        return (self.player1, self.player2)

    def reset(self) -> None:
        """Remet les deux scores à 0."""
        self.player1 = 0
        self.player2 = 0

    def is_game_over(self, winning_score: int) -> bool:
        """Retourne True si l'un des deux scores atteint ou dépasse winning_score."""
        return self.player1 >= winning_score or self.player2 >= winning_score

    def get_winner(self, winning_score: int) -> Optional[int]:
        """Retourne 1 ou 2 si la partie est terminée, sinon None."""
        if not self.is_game_over(winning_score):
            return None
        if self.player1 >= winning_score:
            return 1
        return 2
