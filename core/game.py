"""Orchestration de la simulation : boucle de jeu, IA et états.

Importe ``core.entities``, ``core.physics``, ``core.rules`` et ``core.ai``.
Aucune dépendance graphique : testable via unittest pur.
"""

import copy
from dataclasses import dataclass

from core.ai import AIPlayer
from core.entities import Ball, Paddle, TableBounds
from core.physics import PhysicsEngine
from core.rules import GamePhase, RulesEngine, Score

#: Vitesse de service initiale de la balle (pixels/s).
SERVE_SPEED: float = 320.0
#: Vitesse des raquettes (pixels/s).
PADDLE_SPEED: float = 420.0
#: Largeur des raquettes (pixels).
PADDLE_WIDTH: float = 12.0
#: Marge entre une raquette et son mur (pixels).
PADDLE_MARGIN: float = 24.0
#: Rayon de la balle (pixels).
BALL_RADIUS: float = 8.0
#: Modes de jeu supportés.
MODES: frozenset[str] = frozenset({"vs_ai", "2p", "training"})


class GameError(Exception):
    """Erreur de logique de jeu (classe de base)."""


class InvalidStateError(GameError):
    """État invalide (ex. dt <= 0, mode inconnu, entrée hors contrat)."""


@dataclass(frozen=True)
class MatchResult:
    """Résultat final d'un match (immutable, sérialisable pour la persistance)."""

    p1_sets: int
    p2_sets: int
    winner: int  # 1 ou 2
    duration: float  # secondes


@dataclass
class GameState:
    """Snapshot de l'état courant (``get_state()`` en retourne une copie profonde)."""

    ball: Ball
    left_paddle: Paddle
    right_paddle: Paddle
    score: Score
    phase: GamePhase
    server: int
    elapsed: float


class Game:
    """Partie de ping-pong : physique + règles + IA, indépendante du rendu."""

    def __init__(self, bounds: TableBounds, mode: str = "vs_ai") -> None:
        if mode not in MODES:
            raise InvalidStateError(
                f"mode inconnu: {mode!r} (attendu parmi {sorted(MODES)})"
            )
        self.bounds = bounds
        self.mode = mode
        self.rules = RulesEngine()
        self.physics = PhysicsEngine()
        self.ai_left = AIPlayer()
        self.ai_right = AIPlayer()
        self._init_state()

    def _init_state(self) -> None:
        """(Ré)initialise entités, score, phase, serveur et chrono."""
        paddle_height = max(60.0, self.bounds.height * 0.15)
        self.left_paddle = Paddle(
            x=PADDLE_MARGIN,
            y=(self.bounds.height - paddle_height) / 2.0,
            width=PADDLE_WIDTH,
            height=paddle_height,
            speed=PADDLE_SPEED,
        )
        self.right_paddle = Paddle(
            x=self.bounds.width - PADDLE_MARGIN - PADDLE_WIDTH,
            y=(self.bounds.height - paddle_height) / 2.0,
            width=PADDLE_WIDTH,
            height=paddle_height,
            speed=PADDLE_SPEED,
        )
        self.ball = Ball(
            x=self.bounds.width / 2.0,
            y=self.bounds.height / 2.0,
            vx=0.0,
            vy=0.0,
            radius=BALL_RADIUS,
        )
        self.score = Score(p1_points=0, p2_points=0, p1_sets=0, p2_sets=0)
        self.phase = GamePhase.SERVE
        self.server = self.rules.current_server(self.score)
        self.elapsed = 0.0

    def step(self, dt: float, inputs: dict[str, int]) -> GamePhase:
        """Avance la simulation d'un pas de ``dt`` secondes.

        ``inputs`` : ``{"left": -1|0|1, "right": -1|0|1}``. Applique la
        physique, les règles et l'IA si mode ``vs_ai`` ou ``training``.
        Retourne la phase courante. Lève ``InvalidStateError`` si ``dt <= 0``.
        """
        if dt <= 0:
            raise InvalidStateError(f"dt doit être > 0, reçu {dt!r}")
        if self.phase == GamePhase.MATCH_WON:
            return self.phase
        self.elapsed += dt

        left_input = inputs.get("left", 0)
        right_input = inputs.get("right", 0)
        for name, value in (("left", left_input), ("right", right_input)):
            if value not in (-1, 0, 1):
                raise InvalidStateError(
                    f"inputs[{name!r}] doit être dans {{-1, 0, 1}}, reçu {value!r}"
                )

        # Directions effectives (l'IA pilote la raquette droite en vs_ai,
        # les deux raquettes en training).
        left_ai = self.mode == "training"
        right_ai = self.mode in ("vs_ai", "training")
        left_dir = (
            self.ai_left.compute_direction(self.ball, self.left_paddle, self.bounds)
            if left_ai
            else left_input
        )
        right_dir = (
            self.ai_right.compute_direction(self.ball, self.right_paddle, self.bounds)
            if right_ai
            else right_input
        )
        # Déplacement effectif des raquettes (vitesse cappée pour l'IA).
        left_dt = dt * self.ai_left.max_speed_ratio if left_ai else dt
        right_dt = dt * self.ai_right.max_speed_ratio if right_ai else dt
        self.left_paddle.move(left_dir, left_dt, 0.0, self.bounds.height)
        self.right_paddle.move(right_dir, right_dt, 0.0, self.bounds.height)

        # Service (début de partie, après un point ou après un set).
        if self.phase in (GamePhase.SERVE, GamePhase.POINT_SCORED, GamePhase.SET_WON):
            self.server = self.rules.current_server(self.score)
            self.rules.place_serve(self.ball, self.server, self.bounds)
            self._launch_serve()
            self.phase = GamePhase.PLAYING

        if self.phase == GamePhase.PLAYING:
            self.ball.update(dt)
            self.physics.resolve(self.ball, self.left_paddle, self.right_paddle, self.bounds)
            point = self.rules.check_point(self.ball, self.bounds)
            if point is not None:
                # check_point: 1 = sortie à droite (point pour J2),
                #               2 = sortie à gauche (point pour J1).
                winner = 2 if point == 1 else 1
                self.phase = self.rules.apply_point(self.score, winner)
        return self.phase

    def _launch_serve(self) -> None:
        """Donne une vélocité initiale à la balle après ``place_serve``."""
        direction = 1.0 if self.server == 1 else -1.0
        sign = 1.0 if (self.score.p1_points + self.score.p2_points) % 2 == 0 else -1.0
        self.ball.vx = direction * SERVE_SPEED
        self.ball.vy = sign * SERVE_SPEED * 0.4

    def get_state(self) -> GameState:
        """Retourne une copie profonde de l'état actuel."""
        return GameState(
            ball=copy.deepcopy(self.ball),
            left_paddle=copy.deepcopy(self.left_paddle),
            right_paddle=copy.deepcopy(self.right_paddle),
            score=copy.deepcopy(self.score),
            phase=self.phase,
            server=self.server,
            elapsed=self.elapsed,
        )

    def finish_match(self) -> MatchResult | None:
        """Si phase == MATCH_WON, retourne le MatchResult, sinon None."""
        if self.phase != GamePhase.MATCH_WON:
            return None
        winner = 1 if self.score.p1_sets > self.score.p2_sets else 2
        return MatchResult(
            p1_sets=self.score.p1_sets,
            p2_sets=self.score.p2_sets,
            winner=winner,
            duration=self.elapsed,
        )

    def reset(self) -> None:
        """Réinitialise pour une nouvelle partie (mêmes bounds et mode)."""
        self._init_state()
