import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.mages import Demonist
from cards.base_card import Card
from utils.constant import Resource, CardType


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    demonist = Demonist()
    player.board.append(demonist)
    return engine.state, player, demonist


def make_demon():
    return Card("Démon", cost={}, card_type=CardType.DEMON)


# --- effect1 : 1 LIFE pour récupérer une carte de la défausse ---

def test_recupere_carte_de_la_defausse(setup):
    state, player, demonist = setup
    carte = Card("Carte", cost={})
    player.discard.append(carte)
    player.resources.add(Resource.LIFE, 1)

    ability = demonist.get_abilities()[0]
    with patch.object(player, 'choose_card', return_value=carte):
        ability.execute(state, player)

    assert carte in player.hand
    assert carte not in player.discard
    assert player.resources.resources[Resource.LIFE] == 0


def test_pouvoir1_absent_si_defausse_vide(setup):
    state, player, demonist = setup
    player.resources.add(Resource.LIFE, 1)
    assert player.can_afford(demonist.get_abilities()[0]) is False or \
           not demonist.get_abilities()[0].condition(state, player, demonist)


def test_pouvoir1_absent_si_pas_assez_life(setup):
    state, player, demonist = setup
    player.discard.append(Card("Carte", cost={}))
    assert player.can_afford(demonist.get_abilities()[0]) is False


# --- effect2 : désengager un démon ---

def test_desengage_demon(setup):
    state, player, demonist = setup
    demon = make_demon()
    demon.tap()
    player.board.append(demon)

    ability = demonist.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=demon):
        ability.execute(state, player)

    assert demon.is_tapped is False
    assert demonist.is_tapped is True


def test_pouvoir2_absent_sans_demon_engage(setup):
    state, player, demonist = setup
    # demon non engagé
    demon = make_demon()
    player.board.append(demon)
    assert not demonist.get_abilities()[1].condition(state, player, demonist)


def test_pouvoir2_absent_si_demonist_engage(setup):
    state, player, demonist = setup
    demon = make_demon()
    demon.tap()
    player.board.append(demon)
    demonist.tap()
    assert not demonist.get_abilities()[1].condition(state, player, demonist)


def test_pouvoir2_disponible_avec_demon_engage(setup):
    state, player, demonist = setup
    demon = make_demon()
    demon.tap()
    player.board.append(demon)
    assert demonist.get_abilities()[1].condition(state, player, demonist)
