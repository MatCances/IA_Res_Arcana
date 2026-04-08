import pytest
from unittest.mock import patch
from cards.objects import Divination
from cards.artifacts import ElementaryShard, Phoenix, LightFlask
from game.game_state import GameState
from game.human_player import HumanPlayer
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    obj = Divination()
    card1 = ElementaryShard()
    card2 = Phoenix()
    card3 = LightFlask()
    player.board.append(obj)
    player.deck = [card1, card2, card3]
    player.hand = []
    return state, player, obj, card1, card2, card3


def test_pioche_3_et_defausse_3(setup):
    """Pioche 3 cartes et défausse 3 cartes"""
    state, player, obj, card1, card2, card3 = setup
    # défausse les 3 dans l'ordre : 1, 1, 1
    with patch('builtins.input', side_effect=['1', '1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert len(player.deck) == 0
    assert len(player.hand) == 0
    assert len(player.discard) == 3
    assert obj.is_tapped == True


def test_pioche_vide(setup):
    """Si la pioche est vide, la divination est quand même engagée"""
    state, player, obj, card1, card2, card3 = setup
    player.deck = []
    ability = obj.get_abilities()[0]
    ability.execute(state, player)
    assert obj.is_tapped == True


def test_moins_de_3_cartes(setup):
    """Pioche tout et défausse autant qu'on a pioché"""
    state, player, obj, card1, card2, card3 = setup
    player.deck = [card1, card2]
    with patch('builtins.input', side_effect=['1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert len(player.deck) == 0
    assert len(player.hand) == 0
    assert len(player.discard) == 2
    assert obj.is_tapped == True


def test_peut_defausser_carte_prechee(setup):
    """Le joueur peut défausser une carte qu'il vient de piocher"""
    state, player, obj, card1, card2, card3 = setup
    player.deck = [card1, card2, card3]
    player.hand = []
    with patch('builtins.input', side_effect=['1', '1', '1']):
        ability = obj.get_abilities()[0]
        ability.execute(state, player)
    assert card1 in player.discard or card2 in player.discard or card3 in player.discard