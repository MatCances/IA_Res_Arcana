import pytest
from unittest.mock import patch
from cards.objects import CalmElan
from game.game_state import GameState
from game.player import Player
from utils.constant import Resource


@pytest.fixture
def setup():
    player = Player("Alice")
    state = GameState([player])
    obj = CalmElan()
    player.board.append(obj)
    return state, player, obj


def test_collecte_calm(setup):
    """Le joueur choisit CALM et reçoit 1 CALM"""
    state, player, obj = setup
    with patch('builtins.input', return_value='1'):
        obj.collect_base(state, player)
    assert player.resources.resources[Resource.CALM] == 1
    assert player.resources.resources[Resource.ELAN] == 0


def test_collecte_elan(setup):
    """Le joueur choisit ELAN et reçoit 1 ELAN"""
    state, player, obj = setup
    with patch('builtins.input', return_value='2'):
        obj.collect_base(state, player)
    assert player.resources.resources[Resource.ELAN] == 1
    assert player.resources.resources[Resource.CALM] == 0