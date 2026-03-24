import pytest
from unittest.mock import patch
from cards.monuments import ForgottenDomain, Obelisc
from game.game_state import GameState
from game.player import Player
from utils.constant import GameEvent, Resource

# Prepare le setup pour chaque tests dans ce fichier
@pytest.fixture
def setup():
    player1 = Player("Alice")
    player2 = Player("Bob")
    state = GameState([player1, player2])
    domain = ForgottenDomain()
    obelisc = Obelisc()
    player1.board.append(domain)
    state.monuments = [obelisc]
    return state, player1, player2, domain, obelisc


def test_reaction_autre_joueur(setup):
    """La réaction ne se déclenche pas si c'est un autre joueur qui achète"""
    state, player1, player2, domain, obelisc = setup
    domain.on_event(GameEvent.BUY_MONUMENT, state, player2, monument=obelisc)
    assert domain.resources_on.resources[Resource.GOLD] == 0
    assert domain.is_tapped == False


def test_reaction_achat_autel_lui_meme(setup):
    """La réaction ne se déclenche pas si c'est l'autel lui-même qui est acheté"""
    state, player1, player2, domain, obelisc = setup
    domain.on_event(GameEvent.BUY_MONUMENT, state, player1, monument=domain)
    assert domain.resources_on.resources[Resource.GOLD] == 0
    assert domain.is_tapped == False


def test_reaction_deja_engage(setup):
    """La réaction ne se déclenche pas si la carte est déjà engagée"""
    state, player1, player2, domain, obelisc = setup
    domain.tap()
    domain.on_event(GameEvent.BUY_MONUMENT, state, player1, monument=obelisc)
    assert domain.resources_on.resources[Resource.GOLD] == 0


def test_reaction_declenchee(setup):
    """La réaction se déclenche : +1 GOLD sur la carte, carte engagée"""
    state, player1, player2, domain, obelisc = setup
    with patch('builtins.input', return_value='1'):  # le joueur choisit "Oui"
        domain.on_event(GameEvent.BUY_MONUMENT, state, player1, monument=obelisc)
    assert domain.resources_on.resources[Resource.GOLD] == 1
    assert domain.is_tapped == True


def test_reaction_refusee(setup):
    """La réaction ne se déclenche pas si le joueur refuse"""
    state, player1, player2, domain, obelisc = setup
    with patch('builtins.input', return_value='2'):  # le joueur choisit "Non"
        domain.on_event(GameEvent.BUY_MONUMENT, state, player1, monument=obelisc)
    assert domain.resources_on.resources[Resource.GOLD] == 0
    assert domain.is_tapped == False


def test_score(setup):
    """Score = 1 + nombre de GOLD sur la carte"""
    state, player1, player2, domain, obelisc = setup
    domain.resources_on.add(Resource.GOLD, 3)
    assert domain.score(state, player1) == 4