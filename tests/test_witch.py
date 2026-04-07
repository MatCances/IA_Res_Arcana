import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.mages import Witch
from cards.base_card import Card
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    witch = Witch()
    player.board.append(witch)
    return engine.state, player, witch


# --- collect_base ---

def test_collect_base_choisit_life(setup):
    """Régression : choices doit être une liste, pas un set (TypeError sinon)."""
    state, player, witch = setup
    with patch.object(player, 'choose_resource', return_value=Resource.LIFE):
        witch.collect_base(state, player)
    assert player.resources.resources[Resource.LIFE] == 1
    assert player.resources.resources[Resource.DEATH] == 0


def test_collect_base_choices_est_indexable(setup):
    """Vérifie que choose_resource reçoit bien une liste (pas un set)."""
    state, player, witch = setup
    received = []
    def capture(choices, **_):
        received.append(choices)
        return choices[0]
    with patch.object(player, 'choose_resource', side_effect=capture):
        witch.collect_base(state, player)
    assert isinstance(received[0], list)


def test_collect_base_choisit_death(setup):
    state, player, witch = setup
    with patch.object(player, 'choose_resource', return_value=Resource.DEATH):
        witch.collect_base(state, player)
    assert player.resources.resources[Resource.DEATH] == 1
    assert player.resources.resources[Resource.LIFE] == 0


# --- ability : 2 ressources pour désengager une carte ---

def test_desengage_carte_engagee(setup):
    """Paie 2 ressources et désangage une carte engagée."""
    state, player, witch = setup
    card = Card("test", cost={})
    card.tap()
    player.board.append(card)
    player.resources.add(Resource.ELAN, 2)

    ability = witch.get_abilities()[0]
    with patch.object(player, 'choose_resource', return_value=Resource.ELAN):
        with patch.object(player, 'choose_card', return_value=card):
            ability.execute(state, player)

    assert card.is_tapped is False
    assert player.resources.resources[Resource.ELAN] == 0
    assert witch.is_tapped is True


def test_aucune_carte_engagee(setup):
    """Sans carte engagée, paie quand même 2 ressources et la Sorcière s'engage."""
    state, player, witch = setup
    player.resources.add(Resource.ELAN, 2)

    ability = witch.get_abilities()[0]
    with patch.object(player, 'choose_resource', return_value=Resource.ELAN):
        ability.execute(state, player)

    assert player.resources.resources[Resource.ELAN] == 0
    assert witch.is_tapped is True


def test_pas_assez_ressources(setup):
    """Sans 2 ressources, le pouvoir n'est pas disponible."""
    state, player, witch = setup
    player.resources.add(Resource.ELAN, 1)
    assert player.can_afford(witch.get_abilities()[0]) is False
