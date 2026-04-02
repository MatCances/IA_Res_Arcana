import pytest
from unittest.mock import patch
from cards.scrolls import Recovery
from cards.artifacts import Phoenix, PlanarShadow, Homonculus
from game.game_state import GameState
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.mages import Artificer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    player.resources.add(Resource.ELAN, 2)
    player.resources.add(Resource.LIFE, 1)
    return engine.state, player

def test_no_reduction(setup):
    state, player = setup
    assert player.can_buy(card=Phoenix()) == False

def test_single_reduction(setup):
    state, player = setup
    player.board.append(Artificer())
    assert player.can_buy(card=Phoenix()) == True

    player.resources.remove(Resource.LIFE, 1)
    player.resources.add(Resource.ELAN, 2)
    assert player.can_buy(card=Phoenix()) == True

def test_double_reduction(setup):
    state, player = setup
    player.board.append(Artificer())
    player.board.append(Homonculus())
    player.resources.remove(Resource.ELAN, 1)

    assert player.can_buy(card=Phoenix()) == False
    assert player.can_buy(card=PlanarShadow()) == False

    player.resources.add(Resource.CALM, 1)
    assert player.can_buy(card=PlanarShadow()) == True

    player.resources.remove(Resource.CALM, 1)
    player.resources.add(Resource.DEATH, 1)
    assert player.can_buy(card=PlanarShadow()) == True


    


