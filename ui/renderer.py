"""Rendu graphique du jeu via ``tkinter.Canvas`` (chantier ch3).

Le ``Renderer`` convertit les unités logiques du noyau (``core``) en pixels
grâce à ``scale`` et ``margin``. Il consomme les dataclasses de ``core`` en
lecture seule et ne modifie jamais l'état du jeu.
"""

from __future__ import annotations

import tkinter as tk

from core.entities import Ball, Paddle, TableBounds
from core.game import GameState, MatchResult
from core.rules import Score
from meta.models import GameSettings

#: Couleur du fond du terrain.
BACKGROUND_COLOR: str = "#0b3d20"
#: Couleur du filet et du texte par défaut.
NET_COLOR: str = "#ffffff"
#: Couleur de la balle.
BALL_COLOR: str = "#ffffff"
#: Couleurs des raquettes (gauche / droite).
LEFT_PADDLE_COLOR: str = "#3fa7ff"
RIGHT_PADDLE_COLOR: str = "#ff5a5a"
#: Couleur de surlignage (sélection menu, message de victoire).
HIGHLIGHT_COLOR: str = "#ffd24a"
#: Couleur du texte standard.
TEXT_COLOR: str = "#ffffff"


class Renderer:
    """Dessine l'état du jeu, les menus et l'écran de fin sur un canvas."""

    def __init__(self, canvas: tk.Canvas, scale: float = 1.0, margin: int = 20) -> None:
        """``scale`` convertit unités logiques (core) en pixels ; ``margin`` est
        la marge (pixels) autour du terrain."""
        self.canvas = canvas
        self.scale = scale
        self.margin = margin
        self.bounds: TableBounds | None = None

    def set_bounds(self, bounds: TableBounds) -> None:
        """Fixe les dimensions logiques du terrain (pour le filet centré)."""
        self.bounds = bounds

    def clear(self) -> None:
        """Supprime tous les items du canvas."""
        self.canvas.delete("all")

    def draw_game(self, state: GameState) -> None:
        """Efface puis dessine fond, filet, raquettes, balle et score."""
        self.clear()
        field_w = self._field_width_px()
        field_h = self._field_height_px()
        # Fond (rectangle plein couvrant le terrain).
        self.canvas.create_rectangle(
            self.margin,
            self.margin,
            self.margin + field_w,
            self.margin + field_h,
            fill=BACKGROUND_COLOR,
            outline="",
        )
        # Filet : ligne verticale centrée selon TableBounds.
        net_w = (self.bounds.net_width if self.bounds is not None else 4.0) * self.scale
        center_x = self.margin + field_w / 2.0
        self.canvas.create_line(
            center_x,
            self.margin,
            center_x,
            self.margin + field_h,
            fill=NET_COLOR,
            width=max(1.0, net_w),
        )
        # Raquettes gauche / droite (rectangles colorés).
        self._draw_paddle(state.left_paddle, LEFT_PADDLE_COLOR)
        self._draw_paddle(state.right_paddle, RIGHT_PADDLE_COLOR)
        # Balle (ovale blanc).
        self._draw_ball(state.ball)
        # Score en haut.
        self._draw_score(state.score)

    def draw_title(self, selected_index: int, options: list[str]) -> None:
        """Dessine le menu titre ; l'option ``selected_index`` est surlignée."""
        self.clear()
        center_x = self.margin + self._field_width_px() / 2.0
        self.canvas.create_text(
            center_x,
            self.margin + 60.0,
            text="PING PONG 2D",
            fill=TEXT_COLOR,
            font=("TkDefaultFont", 32, "bold"),
        )
        for index, label in enumerate(options):
            color = HIGHLIGHT_COLOR if index == selected_index else TEXT_COLOR
            self.canvas.create_text(
                center_x,
                self.margin + 180.0 + index * 50.0,
                text=label,
                fill=color,
                font=("TkDefaultFont", 18),
            )

    def draw_game_over(self, result: MatchResult) -> None:
        """Affiche "Player X Wins!" et le score final des sets (ex. "3 - 1")."""
        self.clear()
        center_x = self.margin + self._field_width_px() / 2.0
        self.canvas.create_text(
            center_x,
            self.margin + 200.0,
            text=f"Player {result.winner} Wins!",
            fill=HIGHLIGHT_COLOR,
            font=("TkDefaultFont", 28, "bold"),
        )
        self.canvas.create_text(
            center_x,
            self.margin + 280.0,
            text=f"{result.p1_sets} - {result.p2_sets}",
            fill=TEXT_COLOR,
            font=("TkDefaultFont", 22),
        )

    def draw_options(self, settings: GameSettings) -> None:
        """Affiche les valeurs actuelles des paramètres (volume, sensibilité,
        résolution)."""
        self.clear()
        center_x = self.margin + self._field_width_px() / 2.0
        self.canvas.create_text(
            center_x,
            self.margin + 60.0,
            text="OPTIONS",
            fill=TEXT_COLOR,
            font=("TkDefaultFont", 28, "bold"),
        )
        lines = [
            f"Volume: {settings.volume:.2f}",
            f"Paddle sensitivity: {settings.paddle_sensitivity:.2f}",
            f"Resolution: {settings.window_width} x {settings.window_height}",
            f"Language: {settings.language}",
            "Press Enter to go back",
        ]
        for index, line in enumerate(lines):
            self.canvas.create_text(
                center_x,
                self.margin + 160.0 + index * 40.0,
                text=line,
                fill=TEXT_COLOR,
                font=("TkDefaultFont", 16),
            )

    def _draw_paddle(self, paddle: Paddle, color: str) -> None:
        """Dessine une raquette (rectangle coloré) en coordonnées logiques."""
        self.canvas.create_rectangle(
            self._px(paddle.x),
            self._py(paddle.y),
            self._px(paddle.x + paddle.width),
            self._py(paddle.y + paddle.height),
            fill=color,
            outline="",
        )

    def _draw_ball(self, ball: Ball) -> None:
        """Dessine la balle (ovale blanc) en coordonnées logiques."""
        radius = ball.radius * self.scale
        self.canvas.create_oval(
            self._px(ball.x) - radius,
            self._py(ball.y) - radius,
            self._px(ball.x) + radius,
            self._py(ball.y) + radius,
            fill=BALL_COLOR,
            outline="",
        )

    def _draw_score(self, score: Score) -> None:
        """Dessine le score du set en haut du terrain : "P1: x - y :P2"."""
        self.canvas.create_text(
            self.margin + self._field_width_px() / 2.0,
            self.margin / 2.0,
            text=f"P1: {score.p1_points} - {score.p2_points} :P2",
            fill=TEXT_COLOR,
            font=("TkDefaultFont", 16, "bold"),
        )

    def _px(self, x: float) -> float:
        """Convertit une coordonnée x logique en pixels."""
        return self.margin + x * self.scale

    def _py(self, y: float) -> float:
        """Convertit une coordonnée y logique en pixels."""
        return self.margin + y * self.scale

    def _field_width_px(self) -> float:
        """Largeur du terrain en pixels (selon bounds ou la taille du canvas)."""
        if self.bounds is not None:
            return self.bounds.width * self.scale
        return self.canvas.winfo_width() - 2 * self.margin

    def _field_height_px(self) -> float:
        """Hauteur du terrain en pixels (selon bounds ou la taille du canvas)."""
        if self.bounds is not None:
            return self.bounds.height * self.scale
        return self.canvas.winfo_height() - 2 * self.margin
