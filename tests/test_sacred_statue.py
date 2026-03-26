import pytest
from unittest.mock import patch
from cards.monuments import SacredStatue
from game.game_state import GameState
from game.player import Player
from utils.constant import Resource, GameEvent


@pytest.fixture
def setup():
    player = Player("Alice")
    state = GameState([player])
    statue = SacredStatue()
    player.board.append(statue)
    player.resources.add(Resource.GOLD, 5)
    return state, player, statue


def test_activation_victoire(setup):
    """Le joueur paie 3 GOLD et gagne 3 points"""
    state, player, statue = setup
    with patch('builtins.input', return_value='1'):
        statue.on_event(GameEvent.VICTORY_CHECK, state, player)
    print("pearl de player dans test sacred statue: ", player.resources.resources[Resource.PEARL])
    assert player.resources.resources[Resource.GOLD] == 2
    assert player.points == 3 + 1  # Le point de la statue aussi
    assert statue.is_tapped == True


def test_refus_activation(setup):
    """Le joueur refuse l'activation, rien ne change"""
    state, player, statue = setup
    with patch('builtins.input', return_value='2'):
        statue.on_event(GameEvent.VICTORY_CHECK, state, player)
    assert player.resources.resources[Resource.GOLD] == 5
    assert player.points == 1
    assert statue.is_tapped == False


def test_pas_assez_gold(setup):
    """Pas proposé si le joueur a moins de 3 GOLD"""
    state, player, statue = setup
    player.resources.remove(Resource.GOLD, 3)  # il reste 2 GOLD
    with patch('builtins.input', return_value='1') as mock_input:
        statue.on_event(GameEvent.VICTORY_CHECK, state, player)
    mock_input.assert_not_called()
    assert player.points == 1
    assert statue.is_tapped == False


def test_deja_engagee(setup):
    """Ne se déclenche pas si la statue est déjà engagée"""
    state, player, statue = setup
    statue.tap()
    with patch('builtins.input', return_value='1') as mock_input:
        statue.on_event(GameEvent.VICTORY_CHECK, state, player)
    mock_input.assert_not_called()
    assert player.points == 1


def test_autre_evenement(setup):
    """Ne réagit pas à un événement autre que VICTORY_CHECK"""
    state, player, statue = setup
    with patch('builtins.input', return_value='1') as mock_input:
        statue.on_event(GameEvent.BUY_MONUMENT, state, player)
    mock_input.assert_not_called()
    assert player.points == 1
    assert statue.is_tapped == False


def test_score(setup):
    """Score de base = 1"""
    state, player, statue = setup
    assert statue.score(state, player) == 1