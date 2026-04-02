import pytest
from unittest.mock import patch
from cards.monuments import Oracle
from game.game_state import GameState
from game.human_player import HumanPlayer
from cards.artifacts import ElementaryShard, Phoenix, LightFlask
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    oracle = Oracle()
    card1 = ElementaryShard()
    card2 = Phoenix()
    card3 = LightFlask()
    card4 = Phoenix()  # carte hors top 3
    player.board.append(oracle)
    player.deck = [card1, card2, card3, card4]
    state.monuments = [card1, card2, card3, card4]
    return state, player, oracle, card1, card2, card3, card4


def test_reordonne_deck_joueur(setup):
    """Le joueur réordonne le top 3 de sa pioche"""
    state, player, oracle, card1, card2, card3, card4 = setup
    player.deck = [card1, card2, card3, card4]
    # choisit deck joueur, puis ordre : card3, card1, card2
    with patch('builtins.input', side_effect=['1', '3', '1', '1']):
        ability = oracle.get_abilities()[0]
        ability.execute(state, player)
    assert player.deck[0] == card3
    assert player.deck[1] == card1
    assert player.deck[2] == card2
    assert player.deck[3] == card4  # la 4e carte n'est pas touchée
    assert oracle.is_tapped == True


def test_reordonne_monuments(setup):
    """Le joueur réordonne le top 3 de la pioche des monuments"""
    state, player, oracle, card1, card2, card3, card4 = setup
    state.monuments = [card1, card2, card3, card4]
    # choisit monuments, puis ordre : card2, card3, card1
    with patch('builtins.input', side_effect=['2', '2', '2', '1']):
        ability = oracle.get_abilities()[0]
        ability.execute(state, player)
    assert state.monuments[0] == card2
    assert state.monuments[1] == card3
    assert state.monuments[2] == card1
    assert state.monuments[3] == card4


def test_pioche_vide(setup):
    """Rien ne se passe si la pioche est vide"""
    state, player, oracle, card1, card2, card3, card4 = setup
    player.deck = []
    with patch('builtins.input', return_value='1'):
        ability = oracle.get_abilities()[0]
        ability.execute(state, player)
    assert oracle.is_tapped == False


def test_moins_de_3_cartes(setup):
    """Fonctionne si la pioche a moins de 3 cartes"""
    state, player, oracle, card1, card2, card3, card4 = setup
    player.deck = [card1, card2]
    with patch('builtins.input', side_effect=['1', '2', '1']):
        ability = oracle.get_abilities()[0]
        ability.execute(state, player)
    assert player.deck[0] == card2
    assert player.deck[1] == card1
    assert oracle.is_tapped == True


def test_score(setup):
    """Score = 2"""
    state, player, oracle, card1, card2, card3, card4 = setup
    assert oracle.score(state, player) == 2