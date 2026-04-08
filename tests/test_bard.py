import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.mages import Bard
from cards.base_card import Card
from utils.constant import Resource, CardType


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    bard = Bard()
    player.board.append(bard)
    return engine.state, player, bard


# --- effect1 : obtenir 1 ressource au choix ---

def test_obtient_1_ressource(setup):
    state, player, bard = setup
    ability = bard.get_abilities()[0]
    with patch.object(player, 'choose_resource', return_value=Resource.ELAN):
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 1
    assert bard.is_tapped is True


def test_effet1_pas_gold_ni_pearl(setup):
    """GOLD et PEARL ne sont pas proposés."""
    state, player, bard = setup
    received_choices = []
    def capture(choices, *_args, **_):
        received_choices.append(list(choices))
        return choices[0]

    ability = bard.get_abilities()[0]
    with patch.object(player, 'choose_resource', side_effect=capture):
        ability.execute(state, player)

    for choices in received_choices:
        assert Resource.GOLD not in choices
        assert Resource.PEARL not in choices


def test_effet1_toujours_disponible(setup):
    state, player, bard = setup
    assert bard.get_abilities()[0].condition(state, player, bard) is True


# --- effect2 : défausser créature/démon/dragon pour +2 GOLD ---

def test_defausse_creature_donne_2_gold(setup):
    state, player, bard = setup
    creature = Card("Créature", cost={}, card_type=CardType.CREATURE)
    player.hand.append(creature)

    ability = bard.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=creature):
        ability.execute(state, player)

    assert creature in player.discard
    assert creature not in player.hand
    assert player.resources.resources[Resource.GOLD] == 2
    assert bard.is_tapped is True


def test_defausse_demon_donne_2_gold(setup):
    state, player, bard = setup
    demon = Card("Démon", cost={}, card_type=CardType.DEMON)
    player.hand.append(demon)

    ability = bard.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=demon):
        ability.execute(state, player)

    assert player.resources.resources[Resource.GOLD] == 2


def test_defausse_dragon_donne_2_gold(setup):
    state, player, bard = setup
    dragon = Card("Dragon", cost={}, card_type=CardType.DRAGON)
    player.hand.append(dragon)

    ability = bard.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=dragon):
        ability.execute(state, player)

    assert player.resources.resources[Resource.GOLD] == 2


def test_pouvoir2_absent_sans_creature_demon_dragon_en_main(setup):
    state, player, bard = setup
    assert not bard.get_abilities()[1].condition(state, player, bard)


def test_pouvoir2_disponible_avec_creature_en_main(setup):
    state, player, bard = setup
    player.hand.append(Card("Créature", cost={}, card_type=CardType.CREATURE))
    assert bard.get_abilities()[1].condition(state, player, bard)


def test_pouvoir2_absent_si_bard_engage(setup):
    state, player, bard = setup
    player.hand.append(Card("Créature", cost={}, card_type=CardType.CREATURE))
    bard.tap()
    assert not bard.get_abilities()[1].condition(state, player, bard)
