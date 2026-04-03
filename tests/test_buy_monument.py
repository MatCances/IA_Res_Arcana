import pytest
from cards.monuments import Monument, Obelisc, AbyssalAltar, Library, Pyramid
from game.game_state import GameState
from game.ai_player import AIPlayer
from game.engine import Engine
from game.action import action_buy_monument
from utils.constant import Resource


@pytest.fixture
def setup():
    player = AIPlayer("IA")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    return engine.state, player


def test_achat_monument_visible_paie_4_gold(setup):
    """Acheter un monument visible coûte 4 GOLD"""
    state, player = setup
    monument = Library()
    state.monuments_visible = [monument]
    state.monuments_deck = []
    player.resources.add(Resource.GOLD, 4)

    action = action_buy_monument(state, player)
    action.execute(state, player)

    assert player.resources.resources[Resource.GOLD] == 0
    assert monument in player.board


def test_achat_monument_visible_retire_des_visibles(setup):
    """Acheter un monument visible le retire de monuments_visible"""
    state, player = setup
    monument = Library()
    state.monuments_visible = [monument]
    state.monuments_deck = []
    player.resources.add(Resource.GOLD, 4)

    action = action_buy_monument(state, player)
    action.execute(state, player)

    assert monument not in state.monuments_visible


def test_achat_monument_pioche(setup):
    """Acheter dans la pioche retire le monument de la pioche et l'ajoute au board"""
    state, player = setup
    monument = Library()
    state.monuments_visible = []
    state.monuments_deck = [monument]
    player.resources.add(Resource.GOLD, 4)

    action = action_buy_monument(state, player)
    action.execute(state, player)

    assert monument in player.board
    assert monument not in state.monuments_deck


def test_achat_monument_pas_assez_gold(setup):
    """Sans 4 GOLD, le monument n'apparait pas dans les actions disponibles"""
    state, player = setup
    state.monuments_visible = [Library()]
    state.monuments_deck = []
    player.resources.add(Resource.GOLD, 3)  # manque 1 GOLD

    actions = state.engine.available_actions(player)
    noms = [a.name for a in actions]

    assert "Acheter un monument" not in noms


def test_achat_monument_obelisc_on_buy(setup):
    """L'Obélisque déclenche son on_buy : le joueur reçoit 6 ressources"""
    state, player = setup
    obelisc = Obelisc()
    state.monuments_visible = [obelisc]
    state.monuments_deck = []
    player.resources.add(Resource.GOLD, 4)

    total_avant = player.resources.total

    action = action_buy_monument(state, player)
    action.execute(state, player)

    # a payé 4 GOLD et reçu 6 ressources
    assert player.resources.total == total_avant - 4 + 6


def test_achat_monument_pyramid_score(setup):
    """La Pyramide vaut 3 points"""
    state, player = setup
    pyramid = Pyramid()
    state.monuments_visible = [pyramid]
    state.monuments_deck = []
    player.resources.add(Resource.GOLD, 4)

    action = action_buy_monument(state, player)
    action.execute(state, player)

    assert player.points == 3

def test_achat_monument_deux_visibles(setup):
    """Avec 2 monuments visibles, l'IA en achète un des deux"""
    state, player = setup
    monument1 = Library()
    monument2 = AbyssalAltar()
    state.monuments_visible = [monument1, monument2]
    state.monuments_deck = []
    player.resources.add(Resource.GOLD, 4)

    action = action_buy_monument(state, player)
    action.execute(state, player)

    assert monument1 in player.board or monument2 in player.board
    assert len(state.monuments_visible) == 1  # un seul reste visible
    assert player.resources.resources[Resource.GOLD] == 0