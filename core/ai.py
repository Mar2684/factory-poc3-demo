"""Joueur artificiel : prédiction de trajectoire et déplacement limité.

Importe uniquement ``core.entities`` : aucune dépendance graphique.
"""

from core.entities import Ball, Paddle, TableBounds

#: Seuil temporel (s) utilisé pour le deadzone du déplacement.
_FRAME_DT: float = 1.0 / 60.0


class AIPlayer:
    """IA de ping-pong basée sur la prédiction de trajectoire.

    ``max_speed_ratio`` ∈ ]0, 1] : 0.7 correspond au niveau moyen (70 % de la
    vitesse max de la raquette).
    """

    def __init__(self, max_speed_ratio: float = 0.7) -> None:
        if not 0.0 < max_speed_ratio <= 1.0:
            raise ValueError(
                f"max_speed_ratio doit être dans ]0, 1], reçu {max_speed_ratio!r}"
            )
        self.max_speed_ratio = max_speed_ratio

    def compute_direction(self, ball: Ball, paddle: Paddle, bounds: TableBounds) -> int:
        """Retourne -1, 0 ou 1.

        Prédit la trajectoire de la balle (avec rebonds sur les murs haut/bas)
        pour viser l'intersection avec la ligne x de la raquette. Le
        déplacement effectif est limité à ``max_speed_ratio * paddle.speed``
        (via le deadzone ci-dessous et le dt réduit appliqué par ``Game``).
        """
        is_left = paddle.x < bounds.width / 2.0
        approaching = ball.vx < 0.0 if is_left else ball.vx > 0.0
        if approaching and ball.vx != 0.0:
            # Bord de la raquette tourné vers la balle.
            edge_x = paddle.x + paddle.width if is_left else paddle.x
            t = (edge_x - ball.x) / ball.vx
            if t < 0.0:
                t = 0.0
            target_y = self._predict_y(ball, t, bounds)
        else:
            # Balle qui s'éloigne : retour vers le centre du terrain.
            target_y = bounds.height / 2.0
        # Centre vertical visé pour la raquette.
        target_top = target_y - paddle.height / 2.0
        diff = target_top - paddle.y
        # Deadzone : déplacement inférieur à ce que la raquette peut couvrir
        # en une frame à vitesse cappée -> pas de mouvement.
        deadzone = self.max_speed_ratio * paddle.speed * _FRAME_DT
        if diff > deadzone:
            return 1
        if diff < -deadzone:
            return -1
        return 0

    def _predict_y(self, ball: Ball, t: float, bounds: TableBounds) -> float:
        """Ordonnée de la balle à l'instant t avec rebonds haut/bas."""
        span = bounds.height - 2.0 * ball.radius
        if span <= 0.0:
            return ball.y
        y = (ball.y - ball.radius + ball.vy * t) % (2.0 * span)
        if y > span:
            y = 2.0 * span - y
        return y + ball.radius
