import pytest
from unittest.mock import patch
from cards.objects import Reanimate
from cards.artifacts import ElementaryShard
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = Reanimate()
    card = ElementaryShard()
    player.board.append(obj)
    player.board.append(card)
    player.resources.add(Resource.ELAN, 1)
    card.tap()
    return state, player, obj, card


def test_desengager_carte(setup):
    """Paie 1 ressource et désengager une carte"""
    state, player, obj, card = setup
    with patch('builtins.input', side_effect=['1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert card.is_tapped == False
    assert obj.is_tapped == True


def test_aucune_carte_engagee(setup):
    """Paie la ressource mais rien ne se passe si aucune carte n'est engagée"""
    state, player, obj, card = setup
    card.untap()
    with patch('builtins.input', return_value='1'):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert obj.is_tapped == True


def test_aucune_ressource(setup):
    """Ne peut pas s'activer sans ressource"""
    state, player, obj, card = setup
    player.resources.remove(Resource.ELAN, 1)
    ability = obj.get_abilities()[0]
    assert not player.can_afford(ability)