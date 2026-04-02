import pytest
from cards.monuments import Library
from game.game_state import GameState
from game.human_player import HumanPlayer
from cards.artifacts import ElementaryShard


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    library = Library()
    card1 = ElementaryShard()
    card2 = ElementaryShard()
    player.board.append(library)
    player.deck = [card1, card2]
    return state, player, library, card1, card2


def test_pioche_carte(setup):
    """La carte est piochée depuis la pioche et ajoutée à la main"""
    state, player, library, card1, card2 = setup
    ability = library.get_abilities()[0]
    ability.execute(state, player)
    assert card1 in player.hand
    assert card1 not in player.deck
    assert library.is_tapped == True


def test_pioche_vide(setup):
    """Rien ne se passe si la pioche est vide"""
    state, player, library, card1, card2 = setup
    player.deck = []
    ability = library.get_abilities()[0]
    ability.execute(state, player)
    assert player.hand == []
    assert library.is_tapped == False


def test_score(setup):
    """Score = 1"""
    state, player, library, card1, card2 = setup
    assert library.score(state, player) == 1