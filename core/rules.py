"""Moteur de règles officielles du ping-pong (11 points par set, meilleur des 3 sets).

Importe uniquement ``core.entities`` : aucune dépendance graphique.
"""

from dataclasses import dataclass
from enum import Enum

from core.entities import Ball, TableBounds


class GamePhase(Enum):
    """Phase courante d'une partie."""

    SERVE = "serve"
    PLAYING = "playing"
    POINT_SCORED = "point_scored"
    SET_WON = "set_won"
    MATCH_WON = "match_won"


@dataclass
class Score:
    """Score courant : points du set en cours et sets gagnés."""

    p1_points: int
    p2_points: int
    p1_sets: int
    p2_sets: int


class RulesEngine:
    """Règles officielles : 11 points par set, meilleur des 3 sets (par défaut)."""

    def __init__(self, points_per_set: int = 11, sets_to_win: int = 3) -> None:
        if points_per_set < 1:
            raise ValueError("points_per_set doit être >= 1")
        if sets_to_win < 1:
            raise ValueError("sets_to_win doit être >= 1")
        self.points_per_set = points_per_set
        self.sets_to_win = sets_to_win

    def check_point(self, ball: Ball, bounds: TableBounds) -> int | None:
        """Retourne 1 si la balle sort par la droite (point pour J2),
        2 si elle sort par la gauche (point pour J1), None sinon.

        Ne modifie pas l'état.
        """
        if ball.x - ball.radius > bounds.width:
            return 1
        if ball.x + ball.radius < 0.0:
            return 2
        return None

    def apply_point(self, score: Score, winner: int) -> GamePhase:
        """Incrémente le score et retourne la nouvelle phase.

        Un set est gagné à ``points_per_set`` points avec 2 points d'écart
        (10-10 puis 2 points d'écart inclus). Incrémente les sets en cas de
        victoire de set et réinitialise les points du set. Lève
        ``InvalidStateError`` si ``winner`` ∉ {1, 2}.
        """
        # Import local pour éviter un cycle d'imports (game importe rules).
        from core.game import InvalidStateError

        if winner not in (1, 2):
            raise InvalidStateError(f"winner invalide: {winner!r} (attendu 1 ou 2)")
        if winner == 1:
            score.p1_points += 1
        else:
            score.p2_points += 1
        p1, p2 = score.p1_points, score.p2_points
        set_won = (
            max(p1, p2) >= self.points_per_set and abs(p1 - p2) >= 2
        )
        if set_won:
            if p1 > p2:
                score.p1_sets += 1
            else:
                score.p2_sets += 1
            score.p1_points = 0
            score.p2_points = 0
            if max(score.p1_sets, score.p2_sets) >= self.sets_to_win:
                return GamePhase.MATCH_WON
            return GamePhase.SET_WON
        return GamePhase.POINT_SCORED

    def current_server(self, score: Score) -> int:
        """Retourne 1 ou 2 selon le service alterné.

        Échange de serveur tous les 2 points, tous les 1 point si les deux
        joueurs ont au moins 10 points.
        """
        total = score.p1_points + score.p2_points
        if score.p1_points >= 10 and score.p2_points >= 10:
            return 1 if total % 2 == 0 else 2
        return 1 if (total // 2) % 2 == 0 else 2

    def place_serve(self, ball: Ball, server: int, bounds: TableBounds) -> None:
        """Positionne la balle au centre du côté du serveur, vélocité nulle."""
        if server == 1:
            x = bounds.width / 4.0
        else:
            x = 3.0 * bounds.width / 4.0
        ball.reset(x, bounds.height / 2.0, 0.0, 0.0)
