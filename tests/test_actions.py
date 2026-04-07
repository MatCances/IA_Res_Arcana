import pytest
from unittest.mock import patch
from game.engine import Engine
from game.human_player import HumanPlayer
from game.action import action_pass, action_discard, action_buy_place_of_power
from cards.base_card import Card
from cards.artifacts import Artifact
from cards.place_of_power import DragonsLair
from utils.constant import Resource, GameEvent


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    return engine.state, player


# --- action_pass ---

def test_action_pass_nom(setup):
    state, player = setup
    action = action_pass(state, player)
    assert action.name == "Passer le tour"


def test_action_pass_execute_sans_erreur(setup):
    state, player = setup
    action = action_pass(state, player)
    action.execute(state, player)  # ne doit pas lever d'exception


# --- action_discard ---

def test_action_discard_choisit_gold(setup):
    """Le joueur défausse une carte et choisit 1 GOLD."""
    state, player = setup
    card = Artifact("Artefact", cost={})
    player.hand.append(card)
    with patch.object(player, 'choose_option', return_value=1):
        action = action_discard(state, player, card)
        action.execute(state, player)
    assert card not in player.hand
    assert card in player.discard
    assert player.resources.resources[Resource.GOLD] == 1


def test_action_discard_choisit_2_ressources(setup):
    """Le joueur défausse et choisit 2 ressources libres."""
    state, player = setup
    card = Artifact("Artefact", cost={})
    player.hand.append(card)
    with patch.object(player, 'choose_option', return_value=0):
        with patch.object(player, 'choose_resource', return_value=Resource.ELAN):
            action = action_discard(state, player, card)
            action.execute(state, player)
    assert card in player.discard
    assert player.resources.resources[Resource.ELAN] == 2


# --- action_buy_place_of_power ---

def test_action_buy_place_of_power_paie_le_cout(setup):
    state, player = setup
    place = DragonsLair()
    state.places_of_power = [place]
    player.resources.add(Resource.LIFE, 3)
    player.resources.add(Resource.DEATH, 3)
    player.resources.add(Resource.ELAN, 3)
    player.resources.add(Resource.CALM, 3)

    action = action_buy_place_of_power(state, player, place)
    action.execute(state, player)

    assert player.resources.resources[Resource.LIFE] == 0
    assert player.resources.resources[Resource.DEATH] == 0
    assert place in player.board


def test_action_buy_place_of_power_retire_du_plateau(setup):
    state, player = setup
    place = DragonsLair()
    state.places_of_power = [place]
    player.resources.add(Resource.LIFE, 3)
    player.resources.add(Resource.DEATH, 3)
    player.resources.add(Resource.ELAN, 3)
    player.resources.add(Resource.CALM, 3)

    action = action_buy_place_of_power(state, player, place)
    action.execute(state, player)

    assert place not in state.places_of_power


def test_action_buy_place_of_power_dispatch_event(setup):
    """L'achat dispatche bien l'événement BUY_PLACE_OF_POWER."""
    state, player = setup
    place = DragonsLair()
    state.places_of_power = [place]
    player.resources.add(Resource.LIFE, 3)
    player.resources.add(Resource.DEATH, 3)
    player.resources.add(Resource.ELAN, 3)
    player.resources.add(Resource.CALM, 3)

    events = []
    def fake_dispatch(event, source, **kwargs):
        events.append(event)

    action = action_buy_place_of_power(state, player, place, dispatch=fake_dispatch)
    action.execute(state, player)

    assert GameEvent.BUY_PLACE_OF_POWER in events
