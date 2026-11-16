"""Package meta (chantier ch2) : persistance JSON des scores et configuration.

Réexporte les symboles publics : ``GameSettings``, ``ScoreRecord``,
``ScoreStorage``, ``StorageError``. Aucune dépendance graphique (stdlib).
"""

from meta.models import GameSettings, ScoreRecord
from meta.storage import ScoreStorage, StorageError

__all__ = [
    "GameSettings",
    "ScoreRecord",
    "ScoreStorage",
    "StorageError",
]
