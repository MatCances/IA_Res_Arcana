import pytest
from unittest.mock import patch
from cards.scrolls import Vitality
from cards.artifacts import ElementaryShard
from game.game_state import GameState
from game.player import Player
from utils.constant import Resource
from game.engine import Engine


@pytest.fixture
def setup():
    player = Player("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    vitality = Vitality()
    card = ElementaryShard()
    player.board.append(vitality)
    player.board.append(card)
    player.resources.add(Resource.ELAN, 2)
    card.tap()
    return engine.state, player, vitality, card


def test_desengager_carte(setup):
    """Paie 2 ELAN et désengager une carte"""
    state, player, vitality, card = setup
    with patch('builtins.input', return_value='1'):
        ability = vitality.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert card.is_tapped == False
    assert vitality not in player.board


def test_aucune_carte_engagee(setup):
    """Ne fait rien si aucune carte engagée"""
    state, player, vitality, card = setup
    card.untap()
    ability = vitality.get_abilities()[0]
    ability.execute(state, player)
    assert vitality in player.board


def test_pas_assez_ressources(setup):
    """Ne peut pas s'activer sans 2 ELAN"""
    state, player, vitality, card = setup
    player.resources.remove(Resource.ELAN, 1)
    ability = vitality.get_abilities()[0]
    assert not player.can_afford(ability)


def test_retourne_dans_pool(setup):
    """Le parchemin retourne dans la pile après utilisation"""
    state, player, vitality, card = setup
    with patch('builtins.input', return_value='1'):
        ability = vitality.get_abilities()[0]
        ability.execute(state, player)
    assert vitality in state.engine.available_scrolls