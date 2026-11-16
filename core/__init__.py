"""Noyau de simulation pure du ping-pong 2D (chantier ch1).

Réexporte les symboles publics : logique indépendante de toute bibliothèque
graphique, testable via unittest pur.
"""

from core.ai import AIPlayer
from core.entities import Ball, Paddle, TableBounds
from core.game import Game, GameError, GameState, InvalidStateError, MatchResult
from core.physics import CollisionType, PhysicsEngine
from core.rules import GamePhase, RulesEngine, Score

__all__ = [
    "AIPlayer",
    "Ball",
    "CollisionType",
    "Game",
    "GameError",
    "GamePhase",
    "GameState",
    "InvalidStateError",
    "MatchResult",
    "Paddle",
    "PhysicsEngine",
    "RulesEngine",
    "Score",
    "TableBounds",
]
