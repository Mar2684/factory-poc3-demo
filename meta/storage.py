"""Persistance JSON du chantier ch2 : high scores et paramètres utilisateur.

Stdlib uniquement (``json``, ``pathlib``, ``os``) : aucune dépendance
graphique. Importe ``meta.models`` et ``core.game.MatchResult``.
"""

import json
import os
from pathlib import Path

from core.game import MatchResult
from meta.models import GameSettings, ScoreRecord, utc_now_iso

SCORES_FILENAME: str = "scores.json"
SETTINGS_FILENAME: str = "settings.json"
DATA_DIRNAME: str = "data"


class StorageError(IOError):
    """Échec d'écriture disque non récupérable."""


class ScoreStorage:
    """Stockage JSON des scores et des paramètres dans ``base_dir/data/``."""

    def __init__(self, base_dir: Path) -> None:
        """Crée ``base_dir`` et le sous-répertoire ``data/`` si absents."""
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / DATA_DIRNAME
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(
                f"impossible de créer le répertoire de sauvegarde {self.data_dir}: {exc}"
            ) from exc

    @property
    def _scores_path(self) -> Path:
        return self.data_dir / SCORES_FILENAME

    @property
    def _settings_path(self) -> Path:
        return self.data_dir / SETTINGS_FILENAME

    def load_scores(self) -> list[ScoreRecord]:
        """Lit ``data/scores.json``.

        Retourne une liste vide si le fichier est absent ou si le JSON est
        invalide (aucune exception levée pour un fichier corrompu) ; les
        entrées individuellement invalides sont ignorées.
        """
        try:
            raw = self._scores_path.read_text(encoding="utf-8")
        except OSError:
            return []
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return []
        if not isinstance(data, list):
            return []
        records: list[ScoreRecord] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                records.append(ScoreRecord.from_dict(item))
            except ValueError:
                continue
        return records

    def add_result(self, result: MatchResult, player_name: str = "Player") -> ScoreRecord:
        """Convertit un ``MatchResult`` en ``ScoreRecord`` et le persiste.

        ``p_score`` = sets gagnés par le joueur (p1), ``opp_score`` = sets
        adversaire (p2), ``won`` = ``result.winner == 1``. Écrit le fichier
        et retourne le record créé. Lève ``StorageError`` si l'écriture échoue.
        """
        record = ScoreRecord(
            player_name=player_name,
            p_score=result.p1_sets,
            opp_score=result.p2_sets,
            won=result.winner == 1,
            date_iso=utc_now_iso(),
        )
        records = self.load_scores()
        records.append(record)
        payload = [r.to_dict() for r in records]
        self._write_json(self._scores_path, payload)
        return record

    def load_settings(self) -> GameSettings:
        """Lit ``data/settings.json``.

        Si le fichier est absent, corrompu ou invalide, retourne
        ``GameSettings()`` avec les valeurs par défaut.
        """
        try:
            raw = self._settings_path.read_text(encoding="utf-8")
        except OSError:
            return GameSettings()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return GameSettings()
        if not isinstance(data, dict):
            return GameSettings()
        try:
            return GameSettings.from_dict(data)
        except ValueError:
            return GameSettings()

    def save_settings(self, settings: GameSettings) -> None:
        """Sérialise et écrit ``data/settings.json``.

        Lève ``StorageError`` si l'écriture échoue.
        """
        self._write_json(self._settings_path, settings.to_dict())

    def _write_json(self, path: Path, payload: object) -> None:
        """Écrit ``payload`` en JSON de façon atomique (tmp puis replace)."""
        tmp_path = path.with_name(path.name + ".tmp")
        try:
            with tmp_path.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp_path, path)
        except OSError as exc:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
            raise StorageError(
                f"écriture impossible dans {path}: {exc}"
            ) from exc
