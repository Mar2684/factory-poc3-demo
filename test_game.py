"""Point d'entrée des tests à la racine (voir cahier des charges).

La suite réelle se trouve dans tests/test_game.py ; ce module la réexporte
pour que `python3 -m unittest discover -s . -p "test_*.py" la trouve aussi
depuis la racine du projet.
"""

from tests.test_game import *  # noqa: F401,F403
from tests.test_game import (  # noqa: F401
    TestAIController,
    TestBallPhysics,
    TestGameEngineScoring,
    TestInputHandler,
    TestPaddleMovement,
    TestScoreLogic,
)
