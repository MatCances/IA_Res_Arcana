import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.mages import Tamer
from cards.base_card import Card
from utils.constant import Resource, CardType


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    tamer = Tamer()
    player.board.append(tamer)
    return engine.state, player, tamer


def make_creature():
    c = Card("Créature", cost={}, card_type=CardType.CREATURE)
    return c


# --- effect1 : 1 LIFE pour 3 LIFE sur la Dresseuse ---

def test_1_life_pour_3_life_sur_dresseuse(setup):
    state, player, tamer = setup
    player.resources.add(Resource.LIFE, 1)
    ability = tamer.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.LIFE] == 0
    assert tamer.resources_on.get_amount(Resource.LIFE) == 3
    assert tamer.is_tapped is True


def test_pas_assez_life_pour_effet1(setup):
    state, player, tamer = setup
    assert player.can_afford(tamer.get_abilities()[0]) is False


# --- effect2 : engager une créature pour 2 ressources ---

def test_engage_creature_donne_2_ressources(setup):
    state, player, tamer = setup
    creature = make_creature()
    player.board.append(creature)

    ability = tamer.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=creature):
        with patch.object(player, 'choose_resource', return_value=Resource.ELAN):
            ability.execute(state, player)

    assert creature.is_tapped is True
    assert tamer.is_tapped is True
    assert player.resources.resources[Resource.ELAN] == 2


def test_engage_creature_ressources_choisies_differentes(setup):
    """Le joueur peut choisir 2 ressources différentes."""
    state, player, tamer = setup
    creature = make_creature()
    player.board.append(creature)

    ability = tamer.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=creature):
        with patch.object(player, 'choose_resource', side_effect=[Resource.ELAN, Resource.CALM]):
            ability.execute(state, player)

    assert player.resources.resources[Resource.ELAN] == 1
    assert player.resources.resources[Resource.CALM] == 1


def test_pas_gold_ni_pearl_disponibles(setup):
    """GOLD et PEARL ne peuvent pas être choisis."""
    state, player, tamer = setup
    creature = make_creature()
    player.board.append(creature)

    received_choices = []
    def capture(choices, **_):
        received_choices.append(list(choices))
        return choices[0]

    ability = tamer.get_abilities()[1]
    with patch.object(player, 'choose_card', return_value=creature):
        with patch.object(player, 'choose_resource', side_effect=capture):
            ability.execute(state, player)

    for choices in received_choices:
        assert Resource.GOLD not in choices
        assert Resource.PEARL not in choices


def test_aucune_creature_disponible(setup):
    """Sans créature, la Dresseuse s'engage mais aucune ressource n'est donnée."""
    state, player, tamer = setup
    ability = tamer.get_abilities()[1]
    ability.execute(state, player)
    assert tamer.is_tapped is True
    assert player.resources.total == 0


def test_creature_engagee_ignoree(setup):
    """Une créature déjà engagée n'est pas proposée."""
    state, player, tamer = setup
    creature = make_creature()
    creature.tap()
    player.board.append(creature)

    ability = tamer.get_abilities()[1]
    ability.execute(state, player)  # pas de créature dispo → s'engage sans rien donner

    assert tamer.is_tapped is True
    assert player.resources.total == 0


def test_effet2_gratuit(setup):
    """Le second pouvoir ne coûte rien."""
    state, player, tamer = setup
    assert player.can_afford(tamer.get_abilities()[1]) is True


def test_pouvoir_absent_si_aucune_creature(setup):
    """Sans créature sur le plateau, le pouvoir n'apparaît pas dans les actions dispo."""
    engine = Engine(players=[setup[1]], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state = setup[0]
    engine.state.engine = engine
    actions = engine.available_actions(setup[1])
    noms = [a.name for a in actions]
    assert not any("Engage Dresseuse" in n for n in noms)


def test_pouvoir_absent_si_dresseuse_engagee(setup):
    """Si la Dresseuse est engagée, le pouvoir n'est pas proposé même avec une créature dispo."""
    engine = Engine(players=[setup[1]], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state = setup[0]
    engine.state.engine = engine
    creature = make_creature()
    setup[1].board.append(creature)
    setup[2].tap()  # Dresseuse engagée
    actions = engine.available_actions(setup[1])
    noms = [a.name for a in actions]
    assert not any("Engage Dresseuse" in n for n in noms)


def test_pouvoir_present_si_creature_disponible(setup):
    """Avec une créature non engagée, le pouvoir apparaît dans les actions dispo."""
    engine = Engine(players=[setup[1]], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state = setup[0]
    engine.state.engine = engine
    creature = make_creature()
    setup[1].board.append(creature)
    actions = engine.available_actions(setup[1])
    noms = [a.name for a in actions]
    assert any("Engage Dresseuse" in n for n in noms)
