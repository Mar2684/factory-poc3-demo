"""Moteur de jeu : orchestre un tick complet (entrées -> IA -> physique -> score -> rendu)."""

import random
import tkinter as tk
from typing import Optional

from ai_controller import AIController
from config import Config
from entities import Ball, Paddle
from game_state import GameMode, GameStatus, Score
from input_handler import InputHandler
from renderer import Renderer


class GameEngine:
    """Boucle principale et physique du jeu de ping-pong."""

    def __init__(
        self,
        root: tk.Tk,
        mode: GameMode,
        config: Config,
        renderer: Renderer,
        input_handler: InputHandler,
    ) -> None:
        self.root = root
        self.mode = mode
        self.config = config
        self.renderer = renderer
        self.input_handler = input_handler
        self.status = GameStatus.PLAYING

        self.paddle1 = Paddle(
            config.paddle_margin,
            0,
            config.paddle_width,
            config.paddle_height,
            config.paddle_speed,
            config.paddle_color,
        )
        self.paddle2 = Paddle(
            config.screen_width - config.paddle_margin - config.paddle_width,
            0,
            config.paddle_width,
            config.paddle_height,
            config.paddle_speed,
            config.paddle_color,
        )
        self.ball = Ball(
            0.0,
            0.0,
            config.ball_radius,
            config.ball_speed_x,
            config.ball_speed_y,
            config.ball_color,
        )
        self.score = Score()
        self.ai_controller: Optional[AIController] = (
            AIController(self.paddle2) if mode == GameMode.SOLO else None
        )
        self.reset_positions()

    def reset_positions(self) -> None:
        """Replace les raquettes centrées et la balle au centre, vers la gauche ou la droite au hasard."""
        height = self.config.screen_height
        center_y = height // 2 - self.config.paddle_height // 2
        self.paddle1.set_y(center_y, height)
        self.paddle2.set_y(center_y, height)
        direction = random.choice((-1.0, 1.0))
        self.ball.reset(
            self.config.screen_width / 2.0,
            height / 2.0,
            self.config.ball_speed_x * direction,
            self.config.ball_speed_y,
        )

    def update(self) -> None:
        """Exécute une itération logique complète si la partie est en cours."""
        if self.status != GameStatus.PLAYING:
            return
        height = self.config.screen_height

        direction1 = self.input_handler.get_player1_direction()
        if direction1 == -1:
            self.paddle1.move_up(height)
        elif direction1 == 1:
            self.paddle1.move_down(height)

        if self.mode == GameMode.SOLO and self.ai_controller is not None:
            self.ai_controller.update(self.ball, height)
        else:
            direction2 = self.input_handler.get_player2_direction()
            if direction2 == -1:
                self.paddle2.move_up(height)
            elif direction2 == 1:
                self.paddle2.move_down(height)

        self.ball.move()
        self.handle_collisions()
        self.check_scoring()
        if self.is_game_over():
            self.status = GameStatus.GAME_OVER

    def handle_collisions(self) -> None:
        """Gère les rebonds sur les murs haut/bas et sur les raquettes."""
        height = self.config.screen_height
        ball_x, ball_y = self.ball.get_position()

        if ball_y - self.ball.radius <= 0 and self.ball.speed_y < 0:
            self.ball.reverse_y()
            self.ball.set_position(ball_x, float(self.ball.radius))
        elif ball_y + self.ball.radius >= height and self.ball.speed_y > 0:
            self.ball.reverse_y()
            self.ball.set_position(ball_x, float(height - self.ball.radius))

        if self.ball.speed_x < 0 and self.paddle1.collides_with(ball_x, ball_y, self.ball.radius):
            self.ball.bounce_off_paddle(self.paddle1, height)
        elif self.ball.speed_x > 0 and self.paddle2.collides_with(ball_x, ball_y, self.ball.radius):
            self.ball.bounce_off_paddle(self.paddle2, height)

    def check_scoring(self) -> int:
        """Retourne 1 si la balle sort à droite, 2 si elle sort à gauche, 0 sinon.

        En cas de but, incrémente le score correspondant et replace la balle au centre.
        """
        ball_x, _ball_y = self.ball.get_position()
        if ball_x > self.config.screen_width:
            self.score.increment_player1()
            self.reset_positions()
            return 1
        if ball_x < 0:
            self.score.increment_player2()
            self.reset_positions()
            return 2
        return 0

    def toggle_pause(self) -> None:
        """Inverse l'état entre PLAYING et PAUSED si la partie n'est pas terminée."""
        if self.is_game_over():
            return
        if self.status == GameStatus.PLAYING:
            self.status = GameStatus.PAUSED
        elif self.status == GameStatus.PAUSED:
            self.status = GameStatus.PLAYING

    def is_game_over(self) -> bool:
        """Retourne True si le score indique une victoire selon config.winning_score."""
        return self.score.is_game_over(self.config.winning_score)

    def get_winner(self) -> Optional[int]:
        """Retourne le numéro du gagnant (1 ou 2) si la partie est terminée, sinon None."""
        if not self.is_game_over():
            return None
        return self.score.get_winner(self.config.winning_score)

    def render_frame(self) -> None:
        """Redessine le terrain complet plus les messages d'état (pause / victoire)."""
        self.renderer.clear()
        self.renderer.draw_center_line()
        self.renderer.draw_paddle(self.paddle1)
        self.renderer.draw_paddle(self.paddle2)
        self.renderer.draw_ball(self.ball)
        self.renderer.draw_score(self.score)
        if self.status == GameStatus.PAUSED:
            self.renderer.draw_message("Pause", "Appuyez sur P pour reprendre")
        elif self.status == GameStatus.GAME_OVER:
            winner = self.get_winner()
            self.renderer.draw_message(f"Joueur {winner} gagne !", "Appuyez sur Q pour quitter")
        self.renderer.update_display()

    def run(self) -> None:
        """Lance la boucle récurrente à fréquence fixe."""
        self.root.after(1000 // self.config.fps, self._loop)

    def _loop(self) -> None:
        """Un tick de boucle : pause, mise à jour, rendu, reprogrammation."""
        if self.input_handler.consume_pause_request():
            self.toggle_pause()

        if self.status == GameStatus.PLAYING:
            self.update()

        self.render_frame()

        if self.status == GameStatus.GAME_OVER:
            # partie terminée : on attend la confirmation de sortie (touche Q)
            if self.input_handler.is_key_pressed("q") or self.input_handler.is_key_pressed("Q"):
                try:
                    self.root.destroy()
                except tk.TclError:
                    pass
                return
        try:
            self.root.after(1000 // self.config.fps, self._loop)
        except tk.TclError:
            # la fenêtre a été détruite : on arrête la boucle
            pass
