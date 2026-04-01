import pytest
from unittest.mock import patch
from cards.objects import Protection
from game.game_state import GameState
from game.player import Player
from utils.constant import Resource, GameEvent


@pytest.fixture
def setup():
    player1 = Player("Alice")
    player2 = Player("Bob")
    state = GameState([player1, player2])
    shield = Protection()
    player1.board.append(shield)
    return state, player1, player2, shield


def test_annule_attaque(setup):
    """Le joueur active le bouclier et annule l'attaque"""
    state, player1, player2, shield = setup
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='1'):
        shield.on_event(GameEvent.ATTACK, state, player1, context=context)
    assert context["cancelled"] == True
    assert shield.is_tapped == True


def test_refuse_activation(setup):
    """Le joueur refuse, l'attaque n'est pas annulée"""
    state, player1, player2, shield = setup
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='2'):
        shield.on_event(GameEvent.ATTACK, state, player1, context=context)
    assert context["cancelled"] == False
    assert shield.is_tapped == False


def test_deja_engage(setup):
    """Ne réagit pas si déjà engagé"""
    state, player1, player2, shield = setup
    shield.tap()
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='1') as mock_input:
        shield.on_event(GameEvent.ATTACK, state, player1, context=context)
    mock_input.assert_not_called()
    assert context["cancelled"] == False


def test_autre_evenement(setup):
    """Ne réagit pas à un autre événement"""
    state, player1, player2, shield = setup
    context = {"damage": 2, "cancelled": False}
    with patch('builtins.input', return_value='1') as mock_input:
        shield.on_event(GameEvent.BUY_MONUMENT, state, player1, context=context)
    mock_input.assert_not_called()
    assert context["cancelled"] == False