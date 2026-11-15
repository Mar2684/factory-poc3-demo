"""Configuration centrale du jeu de ping-pong 2D.

Toutes les constantes ajustables sont regroupées dans une dataclass
immuable (frozen) afin de faciliter les tests et le tuning.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Paramètres globaux du jeu (valeurs par défaut : 800x600, victoire à 5)."""

    screen_width: int = 800
    screen_height: int = 600
    paddle_width: int = 15
    paddle_height: int = 90
    paddle_margin: int = 20
    ball_radius: int = 8
    ball_speed_x: float = 5.0
    ball_speed_y: float = 3.0
    paddle_speed: int = 7
    winning_score: int = 5
    fps: int = 60
    bg_color: str = "#0a0a1a"
    paddle_color: str = "#ffffff"
    ball_color: str = "#ffd54a"
    text_color: str = "#ffffff"
