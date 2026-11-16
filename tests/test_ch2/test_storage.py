"""Tests de meta.storage (ScoreStorage) et meta.models (ScoreRecord, GameSettings)."""

import json
import tempfile
import unittest
from pathlib import Path

from core.game import MatchResult
from meta import GameSettings, ScoreRecord, ScoreStorage, StorageError


def make_result(winner: int = 1, p1_sets: int = 3, p2_sets: int = 1) -> MatchResult:
    return MatchResult(p1_sets=p1_sets, p2_sets=p2_sets, winner=winner, duration=123.4)


class TestStorage(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.storage = ScoreStorage(self.base_dir)

    def test_init_creates_data_dir(self) -> None:
        self.assertTrue((self.base_dir / "data").is_dir())

    def test_add_and_load_roundtrip(self) -> None:
        r1 = self.storage.add_result(make_result(winner=1, p1_sets=3, p2_sets=2), "Alice")
        r2 = self.storage.add_result(make_result(winner=2, p1_sets=1, p2_sets=3), "Bob")
        scores = self.storage.load_scores()
        self.assertEqual(len(scores), 2)
        first = scores[0]
        self.assertEqual(first.player_name, "Alice")
        self.assertEqual(first.p_score, 3)
        self.assertEqual(first.opp_score, 2)
        self.assertTrue(first.won)
        self.assertEqual(scores[1].player_name, "Bob")
        self.assertEqual(scores[1].p_score, 1)
        self.assertEqual(scores[1].opp_score, 3)
        self.assertFalse(scores[1].won)
        # Le record retourné est celui persisté, avec une date ISO 8601 valide.
        self.assertEqual(r1.to_dict()["date_iso"], first.date_iso)
        from datetime import datetime

        datetime.fromisoformat(first.date_iso)  # lève ValueError si invalide

    def test_add_result_default_player_name(self) -> None:
        record = self.storage.add_result(make_result())
        self.assertEqual(record.player_name, "Player")
        self.assertEqual(self.storage.load_scores()[0].player_name, "Player")

    def test_load_scores_missing_file_returns_empty(self) -> None:
        self.assertEqual(self.storage.load_scores(), [])

    def test_corrupted_scores_file_returns_empty_list(self) -> None:
        scores_path = self.base_dir / "data" / "scores.json"
        scores_path.write_text("{invalid", encoding="utf-8")
        self.assertEqual(self.storage.load_scores(), [])

    def test_load_settings_default_when_missing(self) -> None:
        settings = self.storage.load_settings()
        self.assertIsInstance(settings, GameSettings)
        self.assertEqual(settings.paddle_sensitivity, 1.0)
        self.assertEqual(settings.window_width, 800)
        self.assertEqual(settings.window_height, 600)
        self.assertEqual(settings.volume, 0.8)
        self.assertEqual(settings.language, "en")

    def test_settings_roundtrip(self) -> None:
        custom = GameSettings(
            paddle_sensitivity=1.5, volume=0.3, window_width=1024, window_height=768, language="fr"
        )
        self.storage.save_settings(custom)
        loaded = self.storage.load_settings()
        self.assertEqual(loaded, custom)

    def test_corrupted_settings_file_returns_defaults(self) -> None:
        settings_path = self.base_dir / "data" / "settings.json"
        settings_path.write_text("not json at all", encoding="utf-8")
        self.assertEqual(self.storage.load_settings(), GameSettings())

    def test_save_settings_writes_valid_json(self) -> None:
        self.storage.save_settings(GameSettings(paddle_sensitivity=2.0))
        raw = (self.base_dir / "data" / "settings.json").read_text(encoding="utf-8")
        data = json.loads(raw)
        self.assertEqual(data["paddle_sensitivity"], 2.0)

    def test_storage_error_on_unwritable_path(self) -> None:
        # base_dir est un fichier : la création du répertoire échoue.
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "a_file"
            file_path.write_text("x", encoding="utf-8")
            with self.assertRaises(StorageError):
                ScoreStorage(file_path / "sub")


class TestModels(unittest.TestCase):
    def test_score_record_to_from_dict_roundtrip(self) -> None:
        record = ScoreRecord(
            player_name="Alice", p_score=3, opp_score=1, won=True, date_iso="2026-11-16T12:00:00+00:00"
        )
        d = record.to_dict()
        self.assertEqual(
            d,
            {
                "player_name": "Alice",
                "p_score": 3,
                "opp_score": 1,
                "won": True,
                "date_iso": "2026-11-16T12:00:00+00:00",
            },
        )
        self.assertEqual(ScoreRecord.from_dict(d), record)
        # Le dict est JSON-compatible.
        self.assertEqual(ScoreRecord.from_dict(json.loads(json.dumps(d))), record)

    def test_score_record_from_dict_missing_field_raises(self) -> None:
        with self.assertRaises(ValueError):
            ScoreRecord.from_dict({"player_name": "A", "p_score": 1, "opp_score": 0, "won": True})
        with self.assertRaises(ValueError):
            ScoreRecord.from_dict(
                {"player_name": "A", "p_score": 1, "opp_score": 0, "won": True, "date_iso": 42}
            )

    def test_game_settings_sensitivity_bounds(self) -> None:
        GameSettings(paddle_sensitivity=0.5)
        GameSettings(paddle_sensitivity=2.0)
        with self.assertRaises(ValueError):
            GameSettings(paddle_sensitivity=0.4)
        with self.assertRaises(ValueError):
            GameSettings(paddle_sensitivity=2.1)


if __name__ == "__main__":
    unittest.main()
