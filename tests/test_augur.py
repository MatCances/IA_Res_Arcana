import pytest
from unittest.mock import patch
from cards.scrolls import Augur
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
    augur = Augur()
    card = ElementaryShard()
    player.board.append(augur)
    player.deck = [card]
    player.resources.add(Resource.CALM, 1)
    return engine.state, player, augur, card


def test_pioche_une_carte(setup):
    """Paie 1 CALM et pioche une carte"""
    state, player, augur, card = setup
    ability = augur.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.CALM] == 0
    assert card in player.hand
    assert len(player.deck) == 0
    assert augur not in player.board
    assert augur in state.scrolls


def test_pioche_vide(setup):
    """Si la pioche est vide on paye quand meme"""
    state, player, augur, card = setup
    player.deck = []
    ability = augur.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.CALM] == 0
    assert augur not in player.board


def test_pas_assez_calm(setup):
    """Ne peut pas s'activer sans CALM"""
    state, player, augur, card = setup
    player.resources.remove(Resource.CALM, 1)
    ability = augur.get_abilities()[0]
    assert not player.can_afford(ability)


def test_condition_absente_si_pioche_vide(setup):
    """La condition est False si la pioche est vide."""
    state, player, augur, card = setup
    player.deck = []
    ability = augur.get_abilities()[0]
    assert not ability.condition(state, player, augur)


def test_condition_presente_si_pioche_non_vide(setup):
    """La condition est True si la pioche contient des cartes."""
    state, player, augur, card = setup
    ability = augur.get_abilities()[0]
    assert ability.condition(state, player, augur)