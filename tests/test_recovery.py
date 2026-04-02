import pytest
from unittest.mock import patch
from cards.scrolls import Recovery
from cards.artifacts import ElementaryShard
from game.game_state import GameState
from game.human_player import HumanPlayer
from game.engine import Engine
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    recovery = Recovery()
    card = ElementaryShard()
    player.board.append(recovery)
    player.discard = [card]
    player.resources.add(Resource.DEATH, 1)
    return engine.state, player, recovery, card


def test_recupere_carte_defausse(setup):
    """Paie 1 DEATH et récupère une carte de la défausse"""
    state, player, recovery, card = setup
    with patch('builtins.input', return_value='1'):
        ability = recovery.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.DEATH] == 0
    assert card in player.hand
    assert card not in player.discard
    assert recovery not in player.board
    assert recovery in state.engine.available_scrolls


def test_defausse_vide(setup):
    """Ne fait rien si la défausse est vide"""
    state, player, recovery, card = setup
    player.discard = []
    ability = recovery.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.DEATH] == 1
    assert recovery in player.board


def test_pas_assez_death(setup):
    """Ne peut pas s'activer sans DEATH"""
    state, player, recovery, card = setup
    player.resources.remove(Resource.DEATH, 1)
    ability = recovery.get_abilities()[0]
    assert not player.can_afford(ability)


def test_retourne_dans_pool(setup):
    """Le parchemin retourne dans la pile après utilisation"""
    state, player, recovery, card = setup
    with patch('builtins.input', return_value='1'):
        ability = recovery.get_abilities()[0]
        ability.execute(state, player)
    assert recovery in state.engine.available_scrolls