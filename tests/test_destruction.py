import pytest
from unittest.mock import patch
from cards.scrolls import Destruction
from cards.artifacts import DwarvenDraw, ElementaryShard
from game.game_state import GameState
from game.human_player import HumanPlayer
from game.engine import Engine
from utils.constant import Resource


@pytest.fixture
def setup():
    player = HumanPlayer("Alice")
    engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
    engine.state.engine = engine
    destruction = Destruction()
    artifact = DwarvenDraw()  # coût : 1 ELAN
    player.board.append(destruction)
    player.board.append(artifact)
    return engine.state, player, destruction, artifact


def test_detruit_artefact_et_recoit_ressources(setup):
    """Détruit un artefact et reçoit son coût en ressources"""
    state, player, destruction, artifact = setup
    # choisit l'artefact (2e carte du board), puis choisit 1 ELAN
    with patch('builtins.input', side_effect=['1', '4']):
        ability = destruction.get_abilities()[0]
        ability.execute(state, player)
    assert artifact not in player.board
    assert artifact in player.discard
    assert player.resources.resources[Resource.ELAN] == 1
    assert destruction not in player.board
    assert destruction in state.scrolls


def test_artefact_cout_zero(setup):
    """Un artefact avec coût 0 ne donne aucune ressource"""
    state, player, destruction, artifact = setup
    free_artifact = ElementaryShard()  # coût : {}
    player.board.append(free_artifact)
    player.board.remove(artifact)
    with patch('builtins.input', return_value='1'):
        ability = destruction.get_abilities()[0]
        ability.execute(state, player)
    assert free_artifact in player.discard
    assert destruction not in player.board


def test_aucun_artefact(setup):
    """Ne fait rien si aucun artefact sur le board"""
    state, player, destruction, artifact = setup
    player.board.remove(artifact)
    ability = destruction.get_abilities()[0]
    ability.execute(state, player)
    assert destruction in player.board


def test_retourne_dans_pool(setup):
    """Le parchemin retourne dans la pile après utilisation"""
    state, player, destruction, artifact = setup
    with patch('builtins.input', side_effect=['1', '1']):
        ability = destruction.get_abilities()[0]
        ability.execute(state, player)
    assert destruction in state.scrolls


def test_condition_absente_si_aucun_artefact(setup):
    """La condition est False s'il n'y a aucun artefact sur le board."""
    state, player, destruction, artifact = setup
    player.board.remove(artifact)
    ability = destruction.get_abilities()[0]
    assert not ability.condition(state, player, destruction)


def test_condition_presente_si_artefact(setup):
    """La condition est True s'il y a un artefact sur le board."""
    state, player, destruction, artifact = setup
    ability = destruction.get_abilities()[0]
    assert ability.condition(state, player, destruction)