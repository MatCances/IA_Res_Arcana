import pytest
from unittest.mock import patch
from cards.artifacts import Phoenix, BoneDragon, PlanarShadow
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
    return engine.state, player


# --- Sans réduction ---

def test_play_sans_reduction_cout_plein(setup):
    """Sans mage, jouer un Phénix coûte 3 ELAN + 1 LIFE au prix plein"""
    state, player = setup
    phoenix = Phoenix()
    player.hand.append(phoenix)
    player.resources.add(Resource.ELAN, 3)
    player.resources.add(Resource.LIFE, 1)

    phoenix.play(state, player)

    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.LIFE] == 0
    assert phoenix in player.board


def test_play_sans_reduction_pas_assez_ressources(setup):
    """Sans mage, jouer un Phénix échoue si les ressources sont insuffisantes"""
    state, player = setup
    phoenix = Phoenix()
    player.hand.append(phoenix)
    player.resources.add(Resource.ELAN, 2)  # manque 1 ELAN

    result = phoenix.play(state, player)

    assert result == False
    assert phoenix not in player.board


# --- Avec Artificier (réduction permanente de 1) ---

def test_play_avec_artificier_joueur_choisit_ressource_a_reduire(setup):
    """Avec l'Artificier, le Phénix coûte 3 ressources au lieu de 4 ;
    le joueur choisit de ne pas payer 1 LIFE"""
    state, player = setup
    phoenix = Phoenix()
    player.hand.append(phoenix)
    player.board.append(Artificer())
    player.resources.add(Resource.ELAN, 3)
    player.resources.add(Resource.LIFE, 1)

    # Le joueur choisit de payer 3 ELAN (et économise le 1 LIFE)
    with patch('builtins.input', side_effect=['1', '1', '1']):
        phoenix.play(state, player)

    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.LIFE] == 1  # non payé grâce à la réduction
    assert phoenix in player.board


def test_play_avec_artificier_reduction_sur_dragon(setup):
    """Avec l'Artificier, le Dragon d'os coûte 4 ressources au lieu de 5"""
    state, player = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    player.board.append(Artificer())
    player.resources.add(Resource.DEATH, 4)
    # Pas de LIFE : le joueur peut quand même payer car la réduction couvre le LIFE

    with patch('builtins.input', side_effect=['1', '1', '1', '1']):
        dragon.play(state, player)

    assert player.resources.resources[Resource.DEATH] == 0
    assert player.resources.resources[Resource.LIFE] == 0
    assert dragon in player.board


def test_play_avec_artificier_carte_non_engagee(setup):
    """L'Artificier n'a pas besoin de s'engager pour réduire le coût"""
    state, player = setup
    phoenix = Phoenix()
    player.hand.append(phoenix)
    artificer = Artificer()
    player.board.append(artificer)
    player.resources.add(Resource.ELAN, 3)

    with patch('builtins.input', side_effect=['1', '1', '1']):
        phoenix.play(state, player)

    assert artificer.is_tapped == False  # toujours désengagé
    assert phoenix in player.board


# --- Avec Draconiste (réduction de 2 sur les dragons, s'engage) ---

def test_play_draconiste_reduit_dragon(setup):
    """La Draconiste réduit le coût d'un dragon de 2 en s'engageant"""
    state, player = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    draconist = Draconist()
    player.board.append(draconist)
    player.resources.add(Resource.DEATH, 3)

    # La Draconiste active son pouvoir : choisit le dragon puis paie 3 ressources (5-2=3)
    with patch('builtins.input', side_effect=['1', '1', '1', '1']):
        ability = draconist.get_abilities()[0]
        ability.execute(state, player)

    assert player.resources.resources[Resource.DEATH] == 0
    assert dragon in player.board
    assert draconist.is_tapped == True  # la Draconiste s'est engagée


def test_play_draconiste_ne_reduit_pas_artefact_non_dragon(setup):
    """La Draconiste ne réduit pas le coût des artefacts non-dragon"""
    state, player = setup
    phoenix = Phoenix()
    player.hand.append(phoenix)
    draconist = Draconist()
    player.board.append(draconist)
    player.resources.add(Resource.ELAN, 3)
    player.resources.add(Resource.LIFE, 1)

    # Joue le Phénix directement (pas via la Draconiste) : coût plein
    phoenix.play(state, player)

    assert player.resources.resources[Resource.ELAN] == 0
    assert player.resources.resources[Resource.LIFE] == 0
    assert draconist.is_tapped == False


# --- Artificier + Draconiste combinés ---

def test_play_artificier_et_draconiste_cumulent(setup):
    """Artificier (-1) + Draconiste (-2) : le Dragon d'os coûte 2 ressources au lieu de 5"""
    state, player = setup
    dragon = BoneDragon()
    player.hand.append(dragon)
    artificer = Artificer()
    draconist = Draconist()
    player.board.append(artificer)
    player.board.append(draconist)
    player.resources.add(Resource.DEATH, 2)

    # La Draconiste active son pouvoir : choisit le dragon puis paie 2 ressources (5-3=2)
    with patch('builtins.input', side_effect=['1', '1', '1']):
        ability = draconist.get_abilities()[0]
        ability.execute(state, player)

    assert player.resources.resources[Resource.DEATH] == 0
    assert dragon in player.board
    assert draconist.is_tapped == True
    assert artificer.is_tapped == False  # l'Artificier ne s'engage pas