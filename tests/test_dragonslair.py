import pytest
from unittest.mock import patch
from cards.place_of_power import DragonsLair
from cards.artifacts import BoneDragon
from cards.mages import Illusionist
from game.game_state import GameState
from game.human_player import HumanPlayer
from game.engine import Engine
from utils.constant import Resource, CardType


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    lair = DragonsLair()
    dragon = BoneDragon()
    player.board.append(lair)
    player.board.append(dragon)
    return engine.state, player, lair, dragon


def test_produit_2_gold(setup):
    """S'engage et produit 2 GOLD"""
    state, player, lair, dragon = setup
    ability = lair.get_abilities()[0]
    ability.execute(state, player)
    assert player.resources.resources[Resource.GOLD] == 2
    assert lair.is_tapped == True


def test_engage_dragon_pose_2_gold(setup):
    """S'engage et engage un dragon pour poser 2 GOLD sur la carte"""
    state, player, lair, dragon = setup
    with patch('builtins.input', return_value='1'):
        ability = lair.get_abilities()[1]
        ability.execute(state, player)
    assert lair.resources_on.resources[Resource.GOLD] == 2
    assert dragon.is_tapped == True
    assert lair.is_tapped == True


def test_aucun_dragon(setup):
    """Ne fait rien si aucun dragon disponible"""
    state, player, lair, dragon = setup
    dragon.tap()
    ability = lair.get_abilities()[1]
    ability.execute(state, player)
    assert lair.resources_on.resources[Resource.GOLD] == 0
    assert lair.is_tapped == False


def test_illusionniste_remplace_dragon(setup):
    """L'illusionniste peut remplacer un dragon en payant 2 ressources"""
    state, player, lair, dragon = setup
    player.board.remove(dragon)
    illusionist = Illusionist()
    player.board.append(illusionist)
    player.resources.add(Resource.ELAN, 2)
    # choisit l'illusionniste, puis paie 2 ELAN
    with patch('builtins.input', side_effect=['1', '1', '1']):
        ability = lair.get_abilities()[1]
        ability.execute(state, player)
    assert lair.resources_on.resources[Resource.GOLD] == 2
    assert illusionist.is_tapped == True
    assert player.resources.resources[Resource.ELAN] == 0


def test_score_gold_sur_carte(setup):
    """Score = nombre de GOLD sur la carte"""
    state, player, lair, dragon = setup
    lair.resources_on.add(Resource.GOLD, 3)
    assert lair.score(state, player) == 3


def test_score_zero_sans_gold(setup):
    """Score = 0 si aucun GOLD sur la carte"""
    state, player, lair, dragon = setup
    assert lair.score(state, player) == 0