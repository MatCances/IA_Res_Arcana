import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.artifacts import Moloss
from utils.constant import Resource, GameEvent


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    moloss = Moloss()
    player.board.append(moloss)
    return engine, player, moloss


# --- réaction à une attaque ---

def test_annule_attaque_en_sengageant(setup):
    """Le Molosse s'engage pour annuler une attaque."""
    engine, player, moloss = setup
    context = {"damage": 2, "cancelled": False}
    with patch.object(player, 'choose_yes_no', return_value=True):
        moloss.on_event(GameEvent.ATTACK, engine.state, player, context=context)
    assert context["cancelled"] is True
    assert moloss.is_tapped is True


def test_refuse_annulation(setup):
    """Le joueur refuse d'engager le Molosse."""
    engine, player, moloss = setup
    context = {"damage": 2, "cancelled": False}
    with patch.object(player, 'choose_yes_no', return_value=False):
        moloss.on_event(GameEvent.ATTACK, engine.state, player, context=context)
    assert context["cancelled"] is False
    assert moloss.is_tapped is False


def test_autre_evenement_ignore(setup):
    """Le Molosse ne réagit pas à un autre événement."""
    engine, player, moloss = setup
    context = {"damage": 2, "cancelled": False}
    with patch.object(player, 'choose_yes_no', return_value=True) as mock:
        moloss.on_event(GameEvent.BUY_MONUMENT, engine.state, player, context=context)
    mock.assert_not_called()
    assert context["cancelled"] is False


# --- pouvoir : se désengager pour 1 ELAN ---

def test_desengage_pour_1_elan(setup):
    """Quand engagé, le Molosse peut se désengager pour 1 ELAN."""
    engine, player, moloss = setup
    moloss.tap()
    player.resources.add(Resource.ELAN, 1)
    ability = moloss.get_abilities()[0]
    ability.execute(engine.state, player)
    assert moloss.is_tapped is False
    assert player.resources.resources[Resource.ELAN] == 0


def test_pas_assez_elan_pour_desengage(setup):
    """Sans ELAN, le pouvoir n'est pas disponible."""
    engine, player, moloss = setup
    moloss.tap()
    assert player.can_afford(moloss.get_abilities()[0]) is False


# --- disponibilité dans les actions ---

def test_pouvoir_disponible_seulement_si_engage(setup):
    """Le pouvoir n'apparaît dans les actions que si le Molosse est engagé."""
    engine, player, moloss = setup
    player.resources.add(Resource.ELAN, 1)

    # non engagé : pouvoir absent
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert not any("désengager le Molosse" in n for n in noms)

    # engagé : pouvoir présent
    moloss.tap()
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert any("désengager le Molosse" in n for n in noms)
