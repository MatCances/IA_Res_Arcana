import pytest
from unittest.mock import patch
from cards.objects import Research
from cards.artifacts import ElementaryShard
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = Research()
    card = ElementaryShard()
    player.board.append(obj)
    player.deck = [card]
    player.resources.add(Resource.ELAN, 1)
    return state, player, obj, card


def test_pioche_une_carte(setup):
    """Paie 1 ressource et pioche une carte"""
    state, player, obj, card = setup
    with patch('builtins.input', return_value='1'):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert card in player.hand
    assert len(player.deck) == 0
    assert obj.is_tapped == True


def test_pioche_vide(setup):
    """Si la pioche est vide, la recherche est quand même engagée"""
    state, player, obj, card = setup
    player.deck = []
    with patch('builtins.input', return_value='1'):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert obj.is_tapped == True
    assert player.resources.resources[Resource.ELAN] == 0


def test_pas_assez_ressources(setup):
    """Ne peut pas s'activer sans ressource"""
    state, player, obj, card = setup
    player.resources.remove(Resource.ELAN, 1)
    ability = obj.get_abilities()[0]
    assert not player.can_afford(ability)