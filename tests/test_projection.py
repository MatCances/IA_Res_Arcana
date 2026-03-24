import pytest
from unittest.mock import patch
from cards.scrolls import Projection
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from cards.mages import Alchemist
from utils.constant import Resource


@pytest.fixture
def setup():
    player = Player("Alice")
    player.mage = Alchemist()
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    projection = Projection()
    player.board.append(projection)
    player.resources.add(Resource.ELAN, 6)
    return engine.state, player, projection


def test_3x_ressources_pour_x_gold(setup):
    """Paie 6 ELAN (3*2) et reçoit 2 GOLD"""
    state, player, projection = setup
    with patch('builtins.input', side_effect=['1', '2']):
        ability = projection.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.GOLD] == 2
    assert projection not in player.board
    assert projection in state.engine.available_scrolls


def test_pas_assez_ressources(setup):
    """Ne peut pas s'activer avec moins de 3 ressources du même type"""
    state, player, projection = setup
    player.resources.remove(Resource.ELAN, 4)  # reste 2 ELAN
    with patch('builtins.input', return_value='1'):
        ability = projection.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.GOLD] == 0
    assert projection in player.board


def test_retourne_dans_pool(setup):
    """Le parchemin retourne dans la pile après utilisation"""
    state, player, projection = setup
    with patch('builtins.input', side_effect=['1', '1']):
        ability = projection.get_abilities()[0]
        ability.execute(state, player)
    assert projection in state.engine.available_scrolls