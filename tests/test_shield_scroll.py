import pytest
from unittest.mock import patch
from cards.scrolls import Shield
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from cards.mages import Alchemist
from utils.constant import GameEvent, Resource


@pytest.fixture
def setup():
    player1 = Player("Alice")
    player2 = Player("Bob")
    player1.mage = Alchemist()
    player2.mage = Alchemist()
    engine = Engine(players=[player1, player2], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    shield = Shield()
    player1.board.append(shield)
    return engine.state, player1, player2, shield


def test_annule_attaque(setup):
    """Le joueur active le bouclier et annule l'attaque"""
    state, player1, player2, shield = setup
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='1'):
        shield.on_event(GameEvent.ATTACK, state, player1, context=context)
    assert context["cancelled"] == True
    assert shield not in player1.board
    assert shield in state.engine.available_scrolls


def test_refuse_activation(setup):
    """Le joueur refuse, l'attaque n'est pas annulée"""
    state, player1, player2, shield = setup
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='2'):
        shield.on_event(GameEvent.ATTACK, state, player1, context=context)
    assert context["cancelled"] == False
    assert shield in player1.board


def test_autre_evenement(setup):
    """Ne réagit pas à un autre événement"""
    state, player1, player2, shield = setup
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='1') as mock_input:
        shield.on_event(GameEvent.BUY_MONUMENT, state, player1, context=context)
    mock_input.assert_not_called()
    assert context["cancelled"] == False