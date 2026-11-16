"""Entités du noyau de simulation : balle, raquettes et dimensions du terrain.

Module purement logique : aucune dépendance graphique, uniquement la stdlib.
Les dataclasses sont mutables ; les consommateurs (ch3) les lisent sans les
modifier, et ``Game.get_state()`` produit des copies profondes.
"""

from dataclasses import dataclass


@dataclass
class Ball:
    """Balle de ping-pong (position, vélocité, rayon) en coordonnées logiques."""

    x: float
    y: float
    vx: float
    vy: float
    radius: float

    def update(self, dt: float) -> None:
        """Avance la position selon la vélocité et dt (secondes)."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def reset(self, x: float, y: float, vx: float, vy: float) -> None:
        """Réinitialise position et vélocité pour un nouveau service."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


@dataclass
class Paddle:
    """Raquette rectangulaire se déplaçant verticalement (pixels/s)."""

    x: float
    y: float
    width: float
    height: float
    speed: float

    def move(self, direction: int, dt: float, min_y: float, max_y: float) -> None:
        """Déplace verticalement selon direction ∈ {-1, 0, 1}.

        La position résultante est clampée entre ``min_y`` et
        ``max_y - height``.
        """
        self.y += direction * self.speed * dt
        self.y = max(min_y, min(self.y, max_y - self.height))

    def get_aabb(self) -> tuple[float, float, float, float]:
        """Retourne (x, y, width, height) pour les tests de collision AABB."""
        return (self.x, self.y, self.width, self.height)


@dataclass
class TableBounds:
    """Dimensions logiques du terrain (indépendantes de la résolution écran)."""

    width: float
    height: float
    net_width: float
    net_height: float
