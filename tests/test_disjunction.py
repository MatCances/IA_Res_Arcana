import pytest
from unittest.mock import patch
from cards.scrolls import Disjunction
from game.game_state import GameState
from game.human_player import HumanPlayer
from game.engine import Engine
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    disjunction = Disjunction()
    player.board.append(disjunction)
    player.resources.add(Resource.GOLD, 1)
    return engine.state, player, disjunction


def test_echange_gold_contre_ressources(setup):
    """Paie 1 GOLD et reçoit 1 ELAN, 1 DEATH, 1 LIFE, 1 CALM"""
    state, player, disjunction = setup
    ability = disjunction.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.GOLD] == 0
    assert player.resources.resources[Resource.ELAN] == 1
    assert player.resources.resources[Resource.DEATH] == 1
    assert player.resources.resources[Resource.LIFE] == 1
    assert player.resources.resources[Resource.CALM] == 1
    assert disjunction not in player.board
    assert disjunction in state.scrolls


def test_pas_assez_gold(setup):
    """Ne peut pas s'activer sans GOLD"""
    state, player, disjunction = setup
    player.resources.remove(Resource.GOLD, 1)
    ability = disjunction.get_abilities()[0]
    assert not player.can_afford(ability)


def test_retourne_dans_pool(setup):
    """Le parchemin retourne dans la pile après utilisation"""
    state, player, disjunction = setup
    ability = disjunction.get_abilities()[0]
    ability.execute(state, player)
    assert disjunction in state.scrolls