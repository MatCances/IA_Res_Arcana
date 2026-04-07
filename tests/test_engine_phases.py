import pytest
from unittest.mock import patch
from game.engine import Engine
from game.human_player import HumanPlayer
from cards.monuments import Temple, Library
from cards.base_card import Card
from cards.artifacts import Artifact
from utils.constant import Resource


@pytest.fixture
def engine_2joueurs():
    p1 = HumanPlayer("Alice")
    p2 = HumanPlayer("Bob")
    engine = Engine(players=[p1, p2], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    return engine, p1, p2


@pytest.fixture
def engine_1joueur():
    p = HumanPlayer("Alice")
    engine = Engine(players=[p], mages=[], artifacts=[], monuments=[],
                    places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    return engine, p


# --- collect_phase ---

def test_collect_phase_collecte_base(engine_1joueur):
    """collect_base de chaque carte est appelée (Temple donne 1 LIFE)."""
    engine, player = engine_1joueur
    player.board.append(Temple())
    engine.collect_phase()
    assert player.resources.resources[Resource.LIFE] == 1


def test_collect_phase_recupere_ressources_stockees(engine_1joueur):
    """Le joueur choisit '1' : toutes les ressources stockées sont récupérées."""
    engine, player = engine_1joueur
    card = Card("test", cost={})
    card.resources_on.add(Resource.GOLD, 2)
    player.board.append(card)
    with patch('builtins.input', return_value='1'):
        engine.collect_phase()
    assert player.resources.resources[Resource.GOLD] == 2
    assert card.resources_on.get_amount(Resource.GOLD) == 0


def test_collect_phase_laisse_ressources_si_refuse(engine_1joueur):
    """Le joueur choisit '2' : les ressources restent sur la carte."""
    engine, player = engine_1joueur
    card = Card("test", cost={})
    card.resources_on.add(Resource.GOLD, 2)
    player.board.append(card)
    with patch('builtins.input', return_value='2'):
        engine.collect_phase()
    assert player.resources.resources[Resource.GOLD] == 0
    assert card.resources_on.get_amount(Resource.GOLD) == 2


# --- untap_all ---

def test_untap_all_desengage_toutes_les_cartes(engine_2joueurs):
    engine, p1, p2 = engine_2joueurs
    card1 = Card("c1", cost={})
    card2 = Card("c2", cost={})
    card1.tap()
    card2.tap()
    p1.board.append(card1)
    p2.board.append(card2)
    engine.untap_all()
    assert card1.is_tapped is False
    assert card2.is_tapped is False


def test_untap_all_ne_plante_pas_si_board_vide(engine_2joueurs):
    engine, p1, p2 = engine_2joueurs
    engine.untap_all()  # ne doit pas lever d'exception


# --- victory_check ---

def test_victory_check_pas_de_gagnant_si_moins_13(engine_2joueurs):
    engine, p1, p2 = engine_2joueurs
    p1.resources.add(Resource.PEARL, 5)
    p2.resources.add(Resource.PEARL, 4)
    result = engine.victory_check()
    assert result is None


def test_victory_check_gagnant_si_13_points(engine_2joueurs):
    engine, p1, p2 = engine_2joueurs
    p1.resources.add(Resource.PEARL, 13)
    result = engine.victory_check()
    assert result == p1


def test_victory_check_egalite(engine_2joueurs):
    engine, p1, p2 = engine_2joueurs
    p1.resources.add(Resource.PEARL, 13)
    p2.resources.add(Resource.PEARL, 13)
    result = engine.victory_check()
    assert result == "draw"


def test_victory_check_reset_bonus_points_si_pas_gagnant(engine_2joueurs):
    """Les bonus_points sont remis à 0 si personne n'atteint 13."""
    engine, p1, p2 = engine_2joueurs
    p1.bonus_points = 3
    p2.bonus_points = 2
    p1.resources.add(Resource.PEARL, 5)
    engine.victory_check()
    assert p1.bonus_points == 0
    assert p2.bonus_points == 0


# --- available_actions ---

def test_available_actions_contient_toujours_passer(engine_1joueur):
    engine, player = engine_1joueur
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert "Passer le tour" in noms


def test_available_actions_jouer_artefact_si_assez_ressources(engine_1joueur):
    engine, player = engine_1joueur

    class SimpleArtifact(Artifact):
        def __init__(self):
            super().__init__("Artefact Simple", cost={Resource.GOLD: 1})

    card = SimpleArtifact()
    player.hand.append(card)
    player.resources.add(Resource.GOLD, 1)
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert f"Jouer {card.name}" in noms


def test_available_actions_pas_artefact_si_pas_assez_ressources(engine_1joueur):
    engine, player = engine_1joueur

    class SimpleArtifact(Artifact):
        def __init__(self):
            super().__init__("Artefact Simple", cost={Resource.GOLD: 2})

    card = SimpleArtifact()
    player.hand.append(card)
    player.resources.add(Resource.GOLD, 1)
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert f"Jouer {card.name}" not in noms


def test_available_actions_acheter_monument_si_assez_gold(engine_1joueur):
    engine, player = engine_1joueur
    engine.state.monuments_visible = [Library()]
    engine.state.monuments_deck = []
    player.resources.add(Resource.GOLD, 4)
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert "Acheter un monument" in noms


def test_available_actions_defausser_cartes_en_main(engine_1joueur):
    engine, player = engine_1joueur
    card = Card("test", cost={})
    player.hand.append(card)
    actions = engine.available_actions(player)
    noms = [a.name for a in actions]
    assert f"Défausser {card.name}" in noms
