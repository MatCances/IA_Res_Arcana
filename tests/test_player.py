import pytest
from game.human_player import HumanPlayer
from game.engine import Engine
from cards.base_card import Card
from cards.monuments import Pyramid, Library
from cards.mages import Artificer
from utils.constant import Resource, CardType
from utils.resource_pool import ResourcePool


@pytest.fixture
def player():
    p = HumanPlayer("Alice")
    return p


@pytest.fixture
def card_gold_4():
    """Carte générique qui coûte 4 GOLD."""
    c = Card("Carte 4 GOLD", cost={Resource.GOLD: 4})
    return c


@pytest.fixture
def card_multi():
    """Carte qui coûte 2 ELAN + 1 LIFE."""
    c = Card("Carte multi", cost={Resource.ELAN: 2, Resource.LIFE: 1})
    return c


# --- can_buy ---

def test_can_buy_true_si_ressources_suffisantes(player, card_gold_4):
    player.resources.add(Resource.GOLD, 4)
    assert player.can_buy(card_gold_4) is True


def test_can_buy_false_si_ressources_insuffisantes(player, card_gold_4):
    player.resources.add(Resource.GOLD, 3)
    assert player.can_buy(card_gold_4) is False


def test_can_buy_multi_ressources(player, card_multi):
    player.resources.add(Resource.ELAN, 2)
    player.resources.add(Resource.LIFE, 1)
    assert player.can_buy(card_multi) is True


def test_can_buy_false_si_une_ressource_manque(player, card_multi):
    player.resources.add(Resource.ELAN, 2)
    # pas de LIFE
    assert player.can_buy(card_multi) is False


def test_can_buy_avec_reduction_artificier(player):
    """L'Artificier réduit de 1 le coût (hors GOLD/PEARL)."""
    card = Card("Artefact", cost={Resource.ELAN: 2, Resource.LIFE: 1})
    player.board.append(Artificer())
    player.resources.add(Resource.ELAN, 2)
    # Sans réduction : manque 1 LIFE. Avec Artificier (-1 sur LIFE) : peut jouer.
    assert player.can_buy(card) is True


def test_can_buy_carte_gratuite(player):
    c = Card("Gratuite", cost={})
    assert player.can_buy(c) is True


# --- can_afford ---

def test_can_afford_true(player):
    from game.ability import Ability
    player.resources.add(Resource.DEATH, 2)
    ability = Ability("test", cost={Resource.DEATH: 2})
    assert player.can_afford(ability) is True


def test_can_afford_false(player):
    from game.ability import Ability
    player.resources.add(Resource.DEATH, 1)
    ability = Ability("test", cost={Resource.DEATH: 2})
    assert player.can_afford(ability) is False


def test_can_afford_cout_vide(player):
    from game.ability import Ability
    ability = Ability("gratuit", cost={})
    assert player.can_afford(ability) is True


# --- points ---

def test_points_perles_comptent(player):
    player.resources.add(Resource.PEARL, 3)
    assert player.points == 3


def test_points_perles_sur_cartes_comptent(player):
    card = Card("test", cost={})
    card.resources_on.add(Resource.PEARL, 2)
    player.board.append(card)
    assert player.points == 2


def test_points_cartes_avec_score(player):
    pyramid = Pyramid()
    player.board.append(pyramid)
    assert player.points == 3


def test_points_cumul_perles_et_cartes(player):
    player.resources.add(Resource.PEARL, 2)
    pyramid = Pyramid()
    player.board.append(pyramid)
    assert player.points == 5


def test_points_bonus_points(player):
    player.bonus_points = 2
    assert player.points == 2


def test_points_zero_sans_rien(player):
    assert player.points == 0


# --- get_applicable_reductions ---

def test_get_applicable_reductions_vide_sans_carte(player):
    card = Card("test", cost={Resource.GOLD: 4})
    assert player.get_applicable_reductions(card) == []


def test_get_applicable_reductions_avec_artificier(player):
    artificer = Artificer()
    player.board.append(artificer)
    card = Card("test", cost={Resource.ELAN: 2})  # CardType.NONE, pas GOLD/PEARL
    reductions = player.get_applicable_reductions(card)
    assert len(reductions) == 1
    assert reductions[0]["value"] == 1
