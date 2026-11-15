"""Contrôleur IA : pilote la raquette du joueur 2 en mode solo."""

import random

from entities import Ball, Paddle


class AIController:
    """Suit la balle avec une imprécision proportionnelle à 1 - difficulty."""

    def __init__(self, paddle: Paddle, difficulty: float = 0.7) -> None:
        self.paddle = paddle
        # difficulté bornée entre 0.0 (lent/imprécis) et 1.0 (parfait)
        self.difficulty = max(0.0, min(1.0, difficulty))

    def update(self, ball: Ball, screen_height: int) -> None:
        """Déplace la raquette verticalement vers la position y de la balle.

        Une erreur aléatoire proportionnelle à (1 - difficulty) est ajoutée
        à la cible ; les bornes de l'écran sont respectées via la raquette.
        """
        _ball_x, ball_y = ball.get_position()
        target_y = ball_y - self.paddle.height / 2.0
        max_error = (1.0 - self.difficulty) * self.paddle.height
        target_y += random.uniform(-max_error, max_error)
        if self.paddle.y > target_y + self.paddle.speed:
            self.paddle.move_up(screen_height)
        elif self.paddle.y < target_y - self.paddle.speed:
            self.paddle.move_down(screen_height)
