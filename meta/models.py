"""Modèles de persistance du chantier ch2 : paramètres utilisateur et scores.

Dataclasses mutables (``GameSettings``) et enregistrement de score
(``ScoreRecord``), sérialisables en JSON via la stdlib uniquement.
"""

from dataclasses import dataclass, fields
from datetime import datetime, timezone

#: Bornes du contrat pour ``GameSettings.paddle_sensitivity``.
MIN_PADDLE_SENSITIVITY: float = 0.5
MAX_PADDLE_SENSITIVITY: float = 2.0


@dataclass
class GameSettings:
    """Paramètres utilisateur persistants.

    Contrat : ``paddle_sensitivity`` doit appartenir à [0.5, 2.0]
    (``ValueError`` levé sinon).
    """

    paddle_sensitivity: float = 1.0
    volume: float = 0.8
    window_width: int = 800
    window_height: int = 600
    language: str = "en"

    def __post_init__(self) -> None:
        if not (MIN_PADDLE_SENSITIVITY <= self.paddle_sensitivity <= MAX_PADDLE_SENSITIVITY):
            raise ValueError(
                f"paddle_sensitivity doit être dans "
                f"[{MIN_PADDLE_SENSITIVITY}, {MAX_PADDLE_SENSITIVITY}], "
                f"reçu {self.paddle_sensitivity!r}"
            )

    def to_dict(self) -> dict[str, object]:
        """Sérialise en dict JSON-compatible."""
        return {
            "paddle_sensitivity": self.paddle_sensitivity,
            "volume": self.volume,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> "GameSettings":
        """Désérialise depuis un dict (champs inconnus ignorés).

        Lève ``ValueError`` si un champ requis est absent ou invalide.
        """
        names = {f.name for f in fields(cls)}
        kwargs: dict[str, object] = {}
        for name in names:
            if name not in d:
                raise ValueError(f"champ manquant dans GameSettings: {name!r}")
            kwargs[name] = d[name]
        try:
            return cls(**kwargs)  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError(f"GameSettings invalide: {exc}") from exc


@dataclass
class ScoreRecord:
    """Entrée d'un score sauvegardé (date au format ISO 8601)."""

    player_name: str
    p_score: int
    opp_score: int
    won: bool
    date_iso: str

    def to_dict(self) -> dict[str, object]:
        """Sérialise en dict JSON-compatible."""
        return {
            "player_name": self.player_name,
            "p_score": self.p_score,
            "opp_score": self.opp_score,
            "won": self.won,
            "date_iso": self.date_iso,
        }

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> "ScoreRecord":
        """Désérialise depuis un dict.

        Lève ``ValueError`` si un champ requis est absent ou de mauvais type.
        """
        required: dict[str, type] = {
            "player_name": str,
            "p_score": int,
            "opp_score": int,
            "won": bool,
            "date_iso": str,
        }
        kwargs: dict[str, object] = {}
        for name, typ in required.items():
            if name not in d:
                raise ValueError(f"champ manquant dans ScoreRecord: {name!r}")
            value = d[name]
            # bool est un sous-type de int : refuser les bool pour les int.
            if not isinstance(value, typ) or (typ is int and isinstance(value, bool)):
                raise ValueError(
                    f"champ {name!r} de ScoreRecord doit être de type "
                    f"{typ.__name__}, reçu {type(value).__name__}"
                )
            kwargs[name] = value
        return cls(**kwargs)  # type: ignore[arg-type]


def utc_now_iso() -> str:
    """Retourne l'instant courant en chaîne ISO 8601 (UTC, aware)."""
    return datetime.now(timezone.utc).isoformat()
