import pytest
from unittest.mock import patch
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.artifacts import Artifact
from cards.base_card import Card
from utils.constant import Resource, CardType


def make_engine(player):
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    return engine


def make_artifact(cost, name="TestCard"):
    return Artifact(name, cost=cost)


def add_reducer(player, value=1, excluded=None, card_types=None):
    """Ajoute une carte avec reduction_effect sur le board du joueur."""
    reducer = Card("Reducer", cost={})
    reducer.reduction_effect = {
        "value": value,
        "excluded": excluded or [],
        "card_type": card_types or [CardType.NONE, CardType.CREATURE, CardType.DEMON, CardType.DRAGON]
    }
    player.board.append(reducer)
    return reducer


# --- Coût fixe sans réduction ---

def test_cout_fixe_paiement_direct():
    """Coût {ELAN: 2} sans réduction : retrait direct."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ELAN: 2})
    player.hand.append(card)
    player.resources.add(Resource.ELAN, 2)

    card.play(engine.state, player)

    assert card in player.board
    assert player.resources.resources[Resource.ELAN] == 0


def test_cout_fixe_multiple_ressources():
    """Coût {ELAN: 1, CALM: 1} sans réduction."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ELAN: 1, Resource.CALM: 1})
    player.hand.append(card)
    player.resources.add(Resource.ELAN, 1)
    player.resources.add(Resource.CALM, 1)

    card.play(engine.state, player)

    assert card in player.board
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.CALM] == 0


# --- Coût avec ANY ---

def test_cout_avec_any_joueur_choisit():
    """Coût {ELAN: 1, ANY: 1} : fixe retiré directement, ANY au choix du joueur."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ELAN: 1, Resource.ANY: 1})
    player.hand.append(card)
    player.resources.add(Resource.ELAN, 1)
    player.resources.add(Resource.CALM, 1)

    with patch.object(player, 'choose_resource', return_value=Resource.CALM):
        card.play(engine.state, player)

    assert card in player.board
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.CALM] == 0


def test_cout_uniquement_any():
    """Coût {ANY: 2} : 2 ressources libres au choix."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ANY: 2})
    player.hand.append(card)
    player.resources.add(Resource.ELAN, 1)
    player.resources.add(Resource.CALM, 1)

    with patch.object(player, 'choose_resource', side_effect=[Resource.ELAN, Resource.CALM]):
        card.play(engine.state, player)

    assert card in player.board
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.CALM] == 0


def test_any_ne_peut_pas_choisir_gold_ni_pearl():
    """Les slots ANY ne permettent pas de payer GOLD ou PEARL."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ANY: 1})
    player.hand.append(card)
    player.resources.add(Resource.ELAN, 1)
    player.resources.add(Resource.GOLD, 5)

    received_choices = []
    def capture(choices, **_):
        received_choices.append(list(choices))
        return choices[0]

    with patch.object(player, 'choose_resource', side_effect=capture):
        card.play(engine.state, player)

    assert Resource.GOLD not in received_choices[0]
    assert Resource.PEARL not in received_choices[0]


# --- Coût fixe avec réduction ---

def test_reduction_joueur_choisit_parmi_ressources_du_cout():
    """Coût {ELAN: 2, CALM: 1}, réduction 1 → joueur paye 2 ressources parmi ELAN/CALM."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ELAN: 2, Resource.CALM: 1})
    player.hand.append(card)
    add_reducer(player, value=1)
    player.resources.add(Resource.ELAN, 2)
    player.resources.add(Resource.CALM, 1)

    # Choisit de payer 2 ELAN (réduit le CALM)
    with patch.object(player, 'choose_resource', side_effect=[Resource.ELAN, Resource.ELAN]):
        card.play(engine.state, player)

    assert card in player.board
    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.CALM] == 1  # non payé


def test_reduction_capee_par_max_ressource():
    """Ne peut pas payer plus que le max d'une ressource dans le coût.
    Coût {ELAN: 1, CALM: 2}, réduction 1 → 2 choix.
    Après avoir payé 1 ELAN (cap atteint), ELAN n'est plus proposé."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ELAN: 1, Resource.CALM: 2})
    player.hand.append(card)
    add_reducer(player, value=1)
    player.resources.add(Resource.ELAN, 3)  # plus que le cap, mais cap = 1
    player.resources.add(Resource.CALM, 2)

    received_choices = []
    def capture(choices, **_):
        received_choices.append(list(choices))
        return choices[0]

    with patch.object(player, 'choose_resource', side_effect=capture):
        card.play(engine.state, player)

    assert len(received_choices) == 2
    assert Resource.ELAN in received_choices[0]   # 1er choix : ELAN dispo (cap = 1, paid = 0)
    assert Resource.ELAN not in received_choices[1]  # 2e choix : ELAN cap atteint (paid = 1 = cap)


# --- Réduction + ANY ---

def test_reduction_sur_fixes_puis_any_libre():
    """Coût {ELAN: 2, ANY: 1}, réduction 1 → paye 1 ELAN (fixe réduit) + 1 libre."""
    player = HumanPlayer("Alice")
    engine = make_engine(player)
    card = make_artifact({Resource.ELAN: 2, Resource.ANY: 1})
    player.hand.append(card)
    add_reducer(player, value=1)
    player.resources.add(Resource.ELAN, 2)
    player.resources.add(Resource.CALM, 1)

    # 1 choix pour le fixe réduit (ELAN), 1 choix pour le ANY (CALM)
    with patch.object(player, 'choose_resource', side_effect=[Resource.ELAN, Resource.CALM]):
        card.play(engine.state, player)

    assert card in player.board
    assert player.resources.resources[Resource.ELAN] == 1  # payé 1 sur 2
    assert player.resources.resources[Resource.CALM] == 0  # payé pour ANY
