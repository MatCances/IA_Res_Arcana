import pytest
from unittest.mock import patch
from cards.objects import Transmutation
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = Transmutation()
    player.board.append(obj)
    player.resources.add(Resource.ELAN, 3)
    return state, player, obj


def test_3_ressources_pour_3_ressources(setup):
    """Paie 3 ressources et reçoit 3 ressources au choix"""
    state, player, obj = setup
    # paie 3 ELAN, reçoit 3 LIFE
    with patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.LIFE] == 3
    assert obj.is_tapped == True


def test_pas_assez_ressources(setup):
    """Ne peut pas s'activer avec moins de 3 ressources"""
    state, player, obj = setup
    player.resources.remove(Resource.ELAN, 1)
    ability = obj.get_abilities()[0]
    assert not player.can_afford(ability)


def test_ne_peut_pas_payer_pearl(setup):
    """Le joueur ne peut pas payer avec des PEARL"""
    state, player, obj = setup
    player.resources.remove(Resource.ELAN, 3)
    player.resources.add(Resource.PEARL, 3)
    ability = obj.get_abilities()[0]
    assert not player.can_afford(ability)