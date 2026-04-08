import pytest
from unittest.mock import patch
from cards.place_of_power import WizardBestiary
from cards.artifacts import BoneDragon
from cards.monuments import SacredStatue
from game.human_player import HumanPlayer
from game.engine import Engine
from utils.constant import Resource, CardType
from cards.base_card import Card


@pytest.fixture
def setup():
    player1 = HumanPlayer("Alice")
    player2 = HumanPlayer("Bob")
    engine = Engine(players=[player1, player2], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    bestiary = WizardBestiary()
    player1.board.append(bestiary)
    return engine, player1, player2, bestiary


# --- Pouvoir 1 : victory check ---

def test_engage_et_lance_victory_check(setup):
    """Le bestiaire s'engage et lance un victory check"""
    engine, player1, player2, bestiary = setup
    ability = bestiary.get_abilities()[0]
    ability.execute(engine.state, player1)
    assert bestiary.is_tapped == True


def test_partie_continue_si_moins_13(setup):
    """Si aucun joueur n'a 13 points, game_over reste False"""
    engine, player1, player2, bestiary = setup
    player1.resources.add(Resource.PEARL, 5)
    player2.resources.add(Resource.PEARL, 7)
    ability = bestiary.get_abilities()[0]
    ability.execute(engine.state, player1)
    assert engine.game_over == False
    assert engine.winner is None


def test_game_over_si_gagnant(setup):
    """Si un joueur a 13+ points, game_over passe à True"""
    engine, player1, player2, bestiary = setup
    
    player1.resources.add(Resource.PEARL, 13)
    ability = bestiary.get_abilities()[0]
    print(f"Player 1 points: {player1.points}")
    ability.execute(engine.state, player1)
    assert engine.game_over == True
    assert engine.winner == player1


def test_game_over_egalite(setup):
    """Si égalité au dessus de 13, game_over et winner = draw"""
    engine, player1, player2, bestiary = setup
    player1.resources.add(Resource.PEARL, 13)
    player2.resources.add(Resource.PEARL, 13)
    ability = bestiary.get_abilities()[0]
    ability.execute(engine.state, player1)
    assert engine.game_over == True
    assert engine.winner == "draw"


def test_gagnant_avec_plus_de_points(setup):
    """Le joueur avec le plus de points gagne"""
    engine, player1, player2, bestiary = setup
    player1.resources.add(Resource.PEARL, 15)
    player1.resources.add(Resource.PEARL, 13)
    ability = bestiary.get_abilities()[0]
    ability.execute(engine.state, player1)
    assert engine.winner == player1


def test_reaction_victory_check(setup):
    """Les cartes de réaction au VICTORY_CHECK sont bien déclenchées"""
    engine, player1, player2, bestiary = setup
    statue = SacredStatue()
    player1.board.append(statue)
    player1.resources.add(Resource.PEARL, 10)
    player1.resources.add(Resource.GOLD, 3)
    with patch('builtins.input', return_value='1'):
        ability = bestiary.get_abilities()[0]
        ability.execute(engine.state, player1)
    assert engine.game_over == True
    assert engine.winner == player1


# --- Pouvoir 2 : récupérer un dragon ---

def test_recupere_dragon_defausse(setup):
    """Paie le coût du dragon (4 DEATH + 1 LIFE) puis 4 ressources libres."""
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()  # coût : {DEATH: 4, LIFE: 1}
    player2.discard.append(dragon)
    player1.resources.add(Resource.ELAN, 4)   # pour les 4 ressources libres
    player1.resources.add(Resource.DEATH, 4)  # pour le coût du dragon
    player1.resources.add(Resource.LIFE, 1)   # pour le coût du dragon

    ability = bestiary.get_abilities()[1]
    with patch.object(player1, 'choose_card', return_value=dragon):
        with patch.object(player1, 'choose_resource', side_effect=[
            Resource.ELAN, Resource.ELAN, Resource.ELAN, Resource.ELAN  # 4 ressources libres
        ]):
            ability.execute(engine.state, player1)

    assert dragon in player1.board
    assert dragon not in player2.discard
    assert player1.resources.resources[Resource.ELAN] == 0
    assert player1.resources.resources[Resource.DEATH] == 0
    assert player1.resources.resources[Resource.LIFE] == 0
    assert bestiary.is_tapped == True


def test_pas_assez_ressources(setup):
    """Ne fait rien si le joueur n'a pas assez de ressources."""
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()  # coût total : 5 ressources + 4 libres = 9
    player2.discard.append(dragon)
    player1.resources.add(Resource.ELAN, 2)  # pas assez
    ability = bestiary.get_abilities()[1]
    with patch.object(player1, 'choose_card', return_value=dragon):
        ability.execute(engine.state, player1)
    assert dragon not in player1.board
    assert bestiary.is_tapped == False


def test_aucun_dragon_en_defausse(setup):
    """Ne fait rien si aucun dragon dans les défausses."""
    engine, player1, player2, bestiary = setup
    ability = bestiary.get_abilities()[1]
    ability.execute(engine.state, player1)
    assert bestiary.is_tapped == False


def test_condition_absente_sans_dragon_en_defausse(setup):
    """La condition du pouvoir 2 est False si aucun dragon dans les défausses."""
    engine, player1, player2, bestiary = setup
    ability = bestiary.get_abilities()[1]
    assert not ability.condition(engine.state, player1, bestiary)


def test_condition_presente_avec_dragon_en_defausse(setup):
    """La condition du pouvoir 2 est True si un dragon est dans une défausse."""
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()
    player2.discard.append(dragon)
    ability = bestiary.get_abilities()[1]
    assert ability.condition(engine.state, player1, bestiary)


def test_4_ressources_libres_pas_pearl(setup):
    """Les 4 ressources libres ne peuvent pas inclure PEARL."""
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()  # coût : {DEATH: 4, LIFE: 1}
    player2.discard.append(dragon)
    player1.resources.add(Resource.ELAN, 4)
    player1.resources.add(Resource.DEATH, 4)
    player1.resources.add(Resource.LIFE, 1)
    player1.resources.add(Resource.PEARL, 5)

    received_choices = []
    def capture(choices, *_args, **_):
        received_choices.append(list(choices))
        return [r for r in choices if r != Resource.PEARL][0]

    ability = bestiary.get_abilities()[1]
    with patch.object(player1, 'choose_card', return_value=dragon):
        with patch.object(player1, 'choose_resource', side_effect=capture):
            ability.execute(engine.state, player1)

    # Vérifier que PEARL n'était jamais dans les choix pour les 4 ressources libres
    for choices in received_choices:
        assert Resource.PEARL not in choices


def test_dragon_avec_cout_any(setup):
    """WindDragon coût {CALM: 4, ANY: 4} : paie les CALM puis choisit pour les ANY."""
    from cards.artifacts import WindDragon
    engine, player1, player2, bestiary = setup
    dragon = WindDragon()
    player2.discard.append(dragon)
    player1.resources.add(Resource.CALM, 4)   # pour le coût fixe CALM
    player1.resources.add(Resource.ELAN, 8)   # 4 pour les ANY du coût + 4 ressources libres

    ability = bestiary.get_abilities()[1]
    with patch.object(player1, 'choose_card', return_value=dragon):
        with patch.object(player1, 'choose_resource', side_effect=[
            Resource.ELAN, Resource.ELAN, Resource.ELAN, Resource.ELAN,  # 4 ANY du coût
            Resource.ELAN, Resource.ELAN, Resource.ELAN, Resource.ELAN,  # 4 ressources libres
        ]):
            ability.execute(engine.state, player1)

    assert dragon in player1.board
    assert player1.resources.resources[Resource.CALM] == 0
    assert player1.resources.resources[Resource.ELAN] == 0


def test_reduction_artificier_sur_cout_dragon(setup):
    """Artificier réduit le coût du dragon de 1, le joueur choisit quelle ressource ne pas payer."""
    from cards.mages import Artificer
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()  # coût : {DEATH: 4, LIFE: 1} → total 5, réduit à 4
    player2.discard.append(dragon)
    artificer = Artificer()
    player1.board.append(artificer)
    player1.resources.add(Resource.DEATH, 4)
    player1.resources.add(Resource.ELAN, 4)  # pour les 4 ressources libres
    # Pas de LIFE → la réduction doit absorber le LIFE

    ability = bestiary.get_abilities()[1]
    with patch.object(player1, 'choose_card', return_value=dragon):
        with patch.object(player1, 'choose_resource', side_effect=[
            Resource.DEATH, Resource.DEATH, Resource.DEATH, Resource.DEATH,  # 4 fixes (réduit de 1)
            Resource.ELAN, Resource.ELAN, Resource.ELAN, Resource.ELAN,       # 4 ressources libres
        ]):
            ability.execute(engine.state, player1)

    assert dragon in player1.board
    assert player1.resources.resources[Resource.DEATH] == 0
    assert player1.resources.resources[Resource.ELAN] == 0


def test_dragon_depuis_sa_propre_defausse(setup):
    """Peut récupérer un dragon de sa propre défausse."""
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()
    player1.discard.append(dragon)
    player1.resources.add(Resource.ELAN, 4)
    player1.resources.add(Resource.DEATH, 4)
    player1.resources.add(Resource.LIFE, 1)

    ability = bestiary.get_abilities()[1]
    with patch.object(player1, 'choose_card', return_value=dragon):
        with patch.object(player1, 'choose_resource', side_effect=[
            Resource.ELAN, Resource.ELAN, Resource.ELAN, Resource.ELAN
        ]):
            ability.execute(engine.state, player1)

    assert dragon in player1.board
    assert dragon not in player1.discard

# --- Score ---
 
def test_score_zero_sans_creature_ni_dragon(setup):
    """Score = 0 sans créature ni dragon"""
    engine, player1, player2, bestiary = setup
    assert bestiary.score(engine.state, player1) == 0
 
 
def test_score_creature(setup):
    """Score = 1 par créature"""
    engine, player1, player2, bestiary = setup
    creature = Card("Créature test", cost={})
    creature.card_type = CardType.CREATURE
    player1.board.append(creature)
    assert bestiary.score(engine.state, player1) == 1
 
 
def test_score_dragon(setup):
    """Score = 2 par dragon"""
    engine, player1, player2, bestiary = setup
    dragon = BoneDragon()
    player1.board.append(dragon)
    assert bestiary.score(engine.state, player1) == 2
 
 
def test_score_mixte(setup):
    """Score = 1 par créature + 2 par dragon"""
    engine, player1, player2, bestiary = setup
    creature = Card("Créature test", cost={})
    creature.card_type = CardType.CREATURE
    dragon = BoneDragon()
    player1.board.append(creature)
    player1.board.append(dragon)
    assert bestiary.score(engine.state, player1) == 3