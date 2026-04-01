import pytest
from unittest.mock import patch
from cards.artifacts import DragonEgg, BoneDragon
from cards.mages import Artificer, Draconist
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from utils.constant import Resource


@pytest.fixture
def setup():
    player = Player("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    egg = DragonEgg()
    player.board.append(egg)
    return engine.state, player, egg


# --- Score ---

def test_score(setup):
    """L'oeuf de dragon vaut 1 point"""
    state, player, egg = setup
    assert egg.score(state, player) == 1


# --- Cas de base ---

def test_pose_dragon_gratuit(setup):
    """Le dragon d'os coûte 5, réduit de 4 -> le joueur paie 1 ressource"""
    state, player, egg = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    player.resources.add(Resource.DEATH, 1)

    with patch('builtins.input', side_effect=['1', '1']):  # choisit le dragon, paie 1 DEATH
        ability = egg.get_abilities()[0]
        ability.execute(state, player)

    assert dragon in player.board
    assert egg not in player.board
    assert egg in player.discard
    assert player.resources.resources[Resource.DEATH] == 0


def test_dragon_totalement_gratuit(setup):
    """Un dragon qui coûte <= 4 est posé gratuitement"""
    state, player, egg = setup

    # On crée un dragon fictif qui coûte 3
    class CheapDragon(BoneDragon):
        def __init__(self):
            super().__init__()
            self.cost = {Resource.DEATH: 3}

    dragon = CheapDragon()
    player.hand.append(dragon)
    # Le joueur n'a aucune ressource : doit quand même pouvoir poser le dragon

    with patch('builtins.input', side_effect=['1']):  # choisit le dragon
        ability = egg.get_abilities()[0]
        ability.execute(state, player)

    assert dragon in player.board
    assert egg not in player.board
    assert egg in player.discard


def test_aucun_dragon_en_main(setup):
    """Sans dragon en main, le pouvoir ne fait rien"""
    state, player, egg = setup

    ability = egg.get_abilities()[0]
    ability.execute(state, player)

    assert egg in player.board  # l'oeuf n'est pas détruit
    assert egg not in player.discard


def test_dragon_en_main_mais_pas_assez_ressources(setup):
    """Un dragon en main mais inabordable même à -4 n'apparaît pas dans les choix"""
    state, player, egg = setup
    dragon = BoneDragon()  # coûte 5, réduit à 1 -> le joueur doit avoir 1 ressource
    player.hand.append(dragon)
    # Le joueur n'a aucune ressource -> dragon filtré par can_buy

    ability = egg.get_abilities()[0]
    ability.execute(state, player)

    assert egg in player.board  # l'oeuf n'est pas détruit
    assert dragon not in player.board


def test_reduction_effect_remis_a_none_apres_execution(setup):
    """Le reduction_effect est bien remis à None après l'exécution"""
    state, player, egg = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    player.resources.add(Resource.DEATH, 1)

    with patch('builtins.input', side_effect=['1', '1']):
        ability = egg.get_abilities()[0]
        ability.execute(state, player)

    assert egg.reduction_effect is None


# --- Combinaison avec Artificier ---

def test_avec_artificier_reduction_cumulee(setup):
    """Oeuf (-4) + Artificier (-1) : le Dragon d'os (coût 5) est posé gratuitement"""
    state, player, egg = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    player.board.append(Artificer())
    # player.resources.add(Resource.DEATH, 1)
    # Le joueur n'a aucune ressource : la réduction totale de 5 couvre tout le coût

    with patch('builtins.input', side_effect=['1', '1']):  # choisit le dragon et paye 1 DEATH
        ability = egg.get_abilities()[0]
        ability.execute(state, player)

    assert dragon in player.board
    assert egg not in player.board
    assert egg in player.discard
    assert player.resources.resources[Resource.DEATH] == 0


# --- Combinaison avec Draconiste ---

def test_avec_draconiste_reduction_cumulee(setup):
    """Oeuf (-4) + Draconiste (-2) : le Dragon d'os (coût 5) est posé gratuitement.
    Draconiste faut l'engager en fait (on peut pas engager 2 cartes en meme temps),
    donc je met 2 artificier à la place"""
    state, player, egg = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    artificer = Artificer()
    player.board.append(artificer)
    player.board.append(artificer)
    # Réduction totale 6 > coût 5 -> gratuit, le joueur n'a besoin d'aucune ressource

    with patch('builtins.input', side_effect=['1']):  # choisit le dragon
        ability = egg.get_abilities()[0]
        ability.execute(state, player)

    assert dragon in player.board
    assert egg not in player.board
    assert egg in player.discard