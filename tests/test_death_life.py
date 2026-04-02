import pytest
from unittest.mock import patch
from cards.objects import DeathLife
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = DeathLife()
    player.board.append(obj)
    return state, player, obj


def test_collecte_death(setup):
    """Le joueur choisit DEATH et reçoit 1 DEATH"""
    state, player, obj = setup
    with patch('builtins.input', return_value='1'):
        obj.collect_base(state, player)
    assert player.resources.resources[Resource.DEATH] == 1
    assert player.resources.resources[Resource.LIFE] == 0


def test_collecte_life(setup):
    """Le joueur choisit LIFE et reçoit 1 LIFE"""
    state, player, obj = setup
    with patch('builtins.input', return_value='2'):
        obj.collect_base(state, player)
    assert player.resources.resources[Resource.LIFE] == 1
    assert player.resources.resources[Resource.DEATH] == 0