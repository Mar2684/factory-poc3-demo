"""Rendu graphique : dessine l'état du jeu sur un Canvas tkinter."""

import tkinter as tk

from config import Config
from entities import Ball, Paddle
from game_state import Score


class Renderer:
    """Dessine les formes géométriques correspondant à l'état courant du jeu."""

    def __init__(self, root: tk.Tk, config: Config) -> None:
        self.root = root
        self.config = config
        self.canvas = tk.Canvas(
            root,
            width=config.screen_width,
            height=config.screen_height,
            bg=config.bg_color,
            highlightthickness=0,
        )
        self.canvas.pack()

    def clear(self) -> None:
        """Supprime tous les éléments graphiques du canvas."""
        self.canvas.delete("all")

    def draw_paddle(self, paddle: Paddle) -> None:
        """Dessine un rectangle plein à la position et aux dimensions de la raquette."""
        x, y, width, height = paddle.get_bounds()
        self.canvas.create_rectangle(x, y, x + width, y + height, fill=paddle.color, outline="")

    def draw_ball(self, ball: Ball) -> None:
        """Dessine un cercle plein centré sur la position de la balle."""
        x, y = ball.get_position()
        r = ball.radius
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=ball.color, outline="")

    def draw_score(self, score: Score) -> None:
        """Affiche en haut au centre le texte "J1 - J2"."""
        score1, score2 = score.get_scores()
        self.canvas.create_text(
            self.config.screen_width // 2,
            30,
            text=f"{score1} - {score2}",
            fill=self.config.text_color,
            font=("Helvetica", 28, "bold"),
        )

    def draw_center_line(self) -> None:
        """Dessine une ligne verticale pointillée au milieu du terrain."""
        middle = self.config.screen_width // 2
        self.canvas.create_line(
            middle,
            0,
            middle,
            self.config.screen_height,
            fill=self.config.text_color,
            dash=(6, 10),
        )

    def draw_message(self, title: str, subtitle: str = "") -> None:
        """Affiche un texte central (titre) et optionnellement un sous-titre en dessous."""
        center_x = self.config.screen_width // 2
        center_y = self.config.screen_height // 2
        self.canvas.create_text(
            center_x,
            center_y - 20,
            text=title,
            fill=self.config.text_color,
            font=("Helvetica", 36, "bold"),
        )
        if subtitle:
            self.canvas.create_text(
                center_x,
                center_y + 30,
                text=subtitle,
                fill=self.config.text_color,
                font=("Helvetica", 16),
            )

    def update_display(self) -> None:
        """Force le rafraîchissement immédiat du canvas."""
        self.canvas.update_idletasks()
