"""Modèle physique du ping-pong : raquettes et balle.

Ce module ne dépend que de la bibliothèque standard (typing, math) et
n'a aucune connaissance du rendu graphique.
"""

import math
from typing import Tuple


class Paddle:
    """Raquette rectangulaire contrôlée par un joueur (ou l'IA)."""

    def __init__(self, x: int, y: int, width: int, height: int, speed: int, color: str) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color

    def move_up(self, screen_height: int) -> None:
        """Monte la raquette sans jamais descendre sous 0."""
        self.y = max(0, self.y - self.speed)

    def move_down(self, screen_height: int) -> None:
        """Descend la raquette sans jamais dépasser screen_height - height."""
        self.y = min(screen_height - self.height, self.y + self.speed)

    def set_y(self, y: int, screen_height: int) -> None:
        """Positionne verticalement la raquette en contraignant y dans [0, screen_height - height]."""
        self.y = max(0, min(int(y), screen_height - self.height))

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Retourne le rectangle de collision (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def collides_with(self, ball_x: float, ball_y: float, ball_radius: int) -> bool:
        """Retourne True si le cercle de la balle intersecte le rectangle de la raquette."""
        closest_x = max(self.x, min(ball_x, self.x + self.width))
        closest_y = max(self.y, min(ball_y, self.y + self.height))
        dx = ball_x - closest_x
        dy = ball_y - closest_y
        return dx * dx + dy * dy <= ball_radius * ball_radius


class Ball:
    """Balle circulaire avec position, vélocité et règles de rebond."""

    def __init__(self, x: float, y: float, radius: int, speed_x: float, speed_y: float, color: str) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color

    def move(self) -> None:
        """Ajoute les composantes de vitesse aux coordonnées courantes."""
        self.x += self.speed_x
        self.y += self.speed_y

    def get_position(self) -> Tuple[float, float]:
        """Retourne les coordonnées (x, y) actuelles."""
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Affecte directement les coordonnées."""
        self.x = x
        self.y = y

    def get_velocity(self) -> Tuple[float, float]:
        """Retourne le couple (speed_x, speed_y)."""
        return (self.speed_x, self.speed_y)

    def reverse_x(self) -> None:
        """Inverse le signe de la vitesse horizontale (rebond sur surface verticale)."""
        self.speed_x = -self.speed_x

    def reverse_y(self) -> None:
        """Inverse le signe de la vitesse verticale (rebond sur surface horizontale)."""
        self.speed_y = -self.speed_y

    def bounce_off_paddle(self, paddle: Paddle, screen_height: int) -> None:
        """Rebond sur une raquette.

        Inverse la vitesse horizontale, recalcule la vitesse verticale
        proportionnellement à la position d'impact relative sur la raquette
        (0 = haut, 1 = bas) pour varier l'angle de rebond, et replace la
        balle à l'extérieur de la raquette pour éviter toute pénétration.
        """
        self.reverse_x()
        if paddle.height > 0:
            relative = (self.y - paddle.y) / paddle.height
        else:
            relative = 0.5
        relative = max(0.0, min(1.0, relative))
        # angle de rebond : -1 (haut) .. +1 (bas), mis à l'échelle de |speed_x|
        self.speed_y = (relative - 0.5) * 2.0 * abs(self.speed_x)
        # replace la balle du côté opposé à sa nouvelle direction
        if self.speed_x > 0:
            self.x = paddle.x + paddle.width + self.radius
        else:
            self.x = paddle.x - self.radius

    def increase_speed(self, factor: float) -> None:
        """Multiplie les deux composantes de vitesse par le facteur fourni."""
        self.speed_x *= factor
        self.speed_y *= factor

    def reset(self, x: float, y: float, speed_x: float, speed_y: float) -> None:
        """Replace la balle aux coordonnées fournies avec la vélocité indiquée."""
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
