"""Tests du moteur de règles (core.rules) — service, points, sets."""

import unittest

from core.entities import Ball, TableBounds
from core.game import InvalidStateError
from core.rules import GamePhase, RulesEngine, Score


def make_bounds() -> TableBounds:
    return TableBounds(width=800.0, height=600.0, net_width=6.0, net_height=200.0)


def make_score(p1: int, p2: int) -> Score:
    return Score(p1_points=p1, p2_points=p2, p1_sets=0, p2_sets=0)


class TestRules(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = RulesEngine()
        self.bounds = make_bounds()

    def test_server_alternation(self):
        """Échange tous les 2 points, tous les 1 point à partir de 10-10."""
        cases = [
            ((0, 0), 1),
            ((1, 0), 1),
            ((2, 0), 2),
            ((2, 1), 2),
            ((2, 2), 1),
            ((10, 10), 1),
            ((11, 10), 2),
            ((11, 11), 1),
            ((12, 11), 2),
        ]
        for (p1, p2), expected in cases:
            with self.subTest(p1=p1, p2=p2):
                self.assertEqual(self.rules.current_server(make_score(p1, p2)), expected)

    def test_set_win_detection(self):
        """11 points pour J1 -> SET_WON et p1_sets == 1."""
        score = make_score(0, 0)
        phase = GamePhase.SERVE
        for _ in range(11):
            phase = self.rules.apply_point(score, 1)
        self.assertEqual(phase, GamePhase.SET_WON)
        self.assertEqual(score.p1_sets, 1)
        self.assertEqual(score.p1_points, 0)  # points remis à zéro pour le set suivant
        self.assertEqual(score.p2_points, 0)

    def test_deuce_requires_two_point_lead(self):
        """10-10 : le set continue ; 12-10 -> SET_WON."""
        score = make_score(0, 0)
        for _ in range(10):
            self.rules.apply_point(score, 1)
            self.rules.apply_point(score, 2)
        self.assertEqual((score.p1_points, score.p2_points), (10, 10))
        phase = self.rules.apply_point(score, 1)  # 11-10
        self.assertEqual(phase, GamePhase.POINT_SCORED)
        phase = self.rules.apply_point(score, 2)  # 11-11
        self.assertEqual(phase, GamePhase.POINT_SCORED)
        self.rules.apply_point(score, 1)  # 12-11
        phase = self.rules.apply_point(score, 1)  # 13-11
        self.assertEqual(phase, GamePhase.SET_WON)
        self.assertEqual(score.p1_sets, 1)

    def test_match_won_after_sets_to_win(self):
        rules = RulesEngine(points_per_set=2, sets_to_win=2)
        score = make_score(0, 0)
        phase = rules.apply_point(score, 1)
        self.assertEqual(phase, GamePhase.POINT_SCORED)
        phase = rules.apply_point(score, 1)  # set 1 pour J1
        self.assertEqual(phase, GamePhase.SET_WON)
        self.assertEqual(score.p1_sets, 1)
        rules.apply_point(score, 2)
        phase = rules.apply_point(score, 2)  # set 2 pour J2 -> 1-1
        self.assertEqual(phase, GamePhase.SET_WON)
        rules.apply_point(score, 1)
        phase = rules.apply_point(score, 1)  # set 3 pour J1 -> match
        self.assertEqual(phase, GamePhase.MATCH_WON)
        self.assertEqual(score.p1_sets, 2)

    def test_apply_point_invalid_winner_raises(self):
        score = make_score(0, 0)
        for bad in (0, 3, -1):
            with self.subTest(winner=bad):
                with self.assertRaises(InvalidStateError):
                    self.rules.apply_point(score, bad)

    def test_check_point_exit_sides(self):
        # Sortie à droite -> 1 (point pour J2) ; sortie à gauche -> 2 (point pour J1).
        ball = Ball(x=810.0, y=300.0, vx=100.0, vy=0.0, radius=8.0)
        self.assertEqual(self.rules.check_point(ball, self.bounds), 1)
        ball = Ball(x=-9.0, y=300.0, vx=-100.0, vy=0.0, radius=8.0)
        self.assertEqual(self.rules.check_point(ball, self.bounds), 2)
        ball = Ball(x=400.0, y=300.0, vx=100.0, vy=0.0, radius=8.0)
        self.assertIsNone(self.rules.check_point(ball, self.bounds))

    def test_check_point_does_not_modify_state(self):
        ball = Ball(x=810.0, y=300.0, vx=100.0, vy=5.0, radius=8.0)
        before = (ball.x, ball.y, ball.vx, ball.vy)
        self.rules.check_point(ball, self.bounds)
        self.assertEqual((ball.x, ball.y, ball.vx, ball.vy), before)

    def test_place_serve(self):
        ball = Ball(x=0.0, y=0.0, vx=50.0, vy=50.0, radius=8.0)
        self.rules.place_serve(ball, 1, self.bounds)
        self.assertEqual((ball.x, ball.y), (200.0, 300.0))
        self.assertEqual((ball.vx, ball.vy), (0.0, 0.0))
        self.rules.place_serve(ball, 2, self.bounds)
        self.assertEqual((ball.x, ball.y), (600.0, 300.0))
        self.assertEqual((ball.vx, ball.vy), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
