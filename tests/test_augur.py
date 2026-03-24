import pytest
from unittest.mock import patch
from cards.scrolls import Augur
from cards.artifacts import ElementaryShard
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from cards.mages import Alchemist
from utils.constant import Resource


@pytest.fixture
def setup():
    player = Player("Alice")
    player.mage = Alchemist()
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
    assert augur in state.engine.available_scrolls


def test_pioche_vide(setup):
    """Ne fait rien si la pioche est vide"""
    state, player, augur, card = setup
    player.deck = []
    ability = augur.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.CALM] == 1
    assert augur in player.board


def test_pas_assez_calm(setup):
    """Ne peut pas s'activer sans CALM"""
    state, player, augur, card = setup
    player.resources.remove(Resource.CALM, 1)
    ability = augur.get_abilities()[0]
    assert not player.can_afford(ability)