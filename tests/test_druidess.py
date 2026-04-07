import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.mages import Druidess
from cards.base_card import Card
from utils.constant import Resource, CardType


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    druidess = Druidess()
    player.board.append(druidess)
    return engine.state, player, druidess


def make_creature():
    return Card("Créature", cost={}, card_type=CardType.CREATURE)


# --- collect_base ---

def test_collect_base_donne_1_life(setup):
    state, player, druidess = setup
    druidess.collect_base(state, player)
    assert player.resources.resources[Resource.LIFE] == 1


# --- ability : désengager une créature ---

def test_desengage_creature(setup):
    state, player, druidess = setup
    creature = make_creature()
    creature.tap()
    player.board.append(creature)

    ability = druidess.get_abilities()[0]
    with patch.object(player, 'choose_card', return_value=creature):
        ability.execute(state, player)

    assert creature.is_tapped is False
    assert druidess.is_tapped is True


def test_pouvoir_absent_sans_creature_engagee(setup):
    state, player, druidess = setup
    creature = make_creature()
    player.board.append(creature)  # non engagée
    assert not druidess.get_abilities()[0].condition(state, player, druidess)


def test_pouvoir_absent_si_druidess_engagee(setup):
    state, player, druidess = setup
    creature = make_creature()
    creature.tap()
    player.board.append(creature)
    druidess.tap()
    assert not druidess.get_abilities()[0].condition(state, player, druidess)


def test_pouvoir_disponible_avec_creature_engagee(setup):
    state, player, druidess = setup
    creature = make_creature()
    creature.tap()
    player.board.append(creature)
    assert druidess.get_abilities()[0].condition(state, player, druidess)


def test_illusionist_non_inclus(setup):
    """La Druidesse ne peut pas désengager un Illusionniste (pas de tap)."""
    state, player, druidess = setup
    illusionist = Card("Illusionniste", cost={}, card_type=CardType.ILLUSIONIST)
    illusionist.tap()
    player.board.append(illusionist)
    assert not druidess.get_abilities()[0].condition(state, player, druidess)
