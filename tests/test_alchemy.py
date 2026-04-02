import pytest
from unittest.mock import patch
from cards.objects import Alchemy
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = Alchemy()
    player.board.append(obj)
    player.resources.add(Resource.ELAN, 4)
    return state, player, obj


def test_4_ressources_pour_2_gold(setup):
    """Paie 4 ressources et reçoit 2 GOLD"""
    state, player, obj = setup
    with patch('builtins.input', side_effect=['1', '1', '1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.GOLD] == 2
    assert obj.is_tapped == True


def test_pas_assez_ressources(setup):
    """Ne peut pas s'activer avec moins de 4 ressources"""
    state, player, obj = setup
    player.resources.remove(Resource.ELAN, 2)
    ability = obj.get_abilities()[0]
    assert not player.can_afford(ability)