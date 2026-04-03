import pytest
from unittest.mock import patch, MagicMock
from cards.objects import Inscription
from cards.scrolls import Vitality
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = Inscription()
    scroll = Vitality()
    player.board.append(obj)
    player.resources.add(Resource.ELAN, 1)
    engine = MagicMock()
    engine.available_scrolls = [scroll]
    state.scrolls = [scroll]
    state.engine = engine
    return state, player, obj, scroll


def test_prend_parchemin(setup):
    """Paie 1 ressource et ajoute un parchemin au board"""
    state, player, obj, scroll = setup
    with patch('builtins.input', side_effect=['1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert scroll in player.board
    assert scroll not in state.scrolls
    assert player.resources.resources[Resource.ELAN] == 0
    assert obj.is_tapped == True


def test_aucun_parchemin_disponible(setup):
    """Ne fait rien si aucun parchemin disponible"""
    state, player, obj, scroll = setup
    state.scrolls = []
    with patch('builtins.input', return_value='1') as mock_input:
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    mock_input.assert_not_called()
    assert obj.is_tapped == False
    assert player.resources.resources[Resource.ELAN] == 1


def test_pas_assez_ressources(setup):
    """Ne peut pas s'activer sans ressource"""
    state, player, obj, scroll = setup
    player.resources.remove(Resource.ELAN, 1)
    ability = obj.get_abilities()[0]
    assert not player.can_afford(ability)