import pytest
from unittest.mock import patch
from cards.monuments import Laboratory
from game.game_state import GameState
from game.human_player import HumanPlayer
from cards.artifacts import ElementaryShard
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    state = GameState([player])
    laboratory = Laboratory()
    card = ElementaryShard()
    player.board.append(laboratory)
    player.board.append(card)
    player.resources.add(Resource.ELAN, 1)
    return state, player, laboratory, card


def test_pose_ressource_sur_carte(setup):
    """La ressource est retirée du joueur et posée sur la carte choisie"""
    state, player, laboratory, card = setup
    # choisit ELAN (1er choix), puis la 2ème carte du board (ElementaryShard)
    with patch('builtins.input', side_effect=['1', '2']):
        ability = laboratory.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert card.resources_on.resources[Resource.ELAN] == 1
    assert laboratory.is_tapped == True


def test_aucune_ressource(setup):
    """Rien ne se passe si le joueur n'a aucune ressource"""
    state, player, laboratory, card = setup
    player.resources.remove(Resource.ELAN, 1)
    ability = laboratory.get_abilities()[0]
    ability.execute(state, player)
    assert laboratory.is_tapped == False


def test_pose_ressource_sur_lui_meme(setup):
    """La ressource peut être posée sur le laboratoire lui-même"""
    state, player, laboratory, card = setup
    player.board.remove(card)
    # seul le laboratory est sur le board, on choisit ELAN puis le laboratory
    with patch('builtins.input', side_effect=['1', '1']):
        ability = laboratory.get_abilities()[0]
        ability.execute(state, player)
    assert player.resources.resources[Resource.ELAN] == 0
    assert laboratory.resources_on.resources[Resource.ELAN] == 1
    assert laboratory.is_tapped == True


def test_score(setup):
    """Score = 1"""
    state, player, laboratory, card = setup
    assert laboratory.score(state, player) == 1
