import pytest
from unittest.mock import patch
from cards.artifacts import BoneDragon
from cards.monuments import GreatWall
from game.game_state import GameState
from game.engine import Engine
from game.player import Player
from cards.mages import Alchemist
from utils.constant import Resource, GameEvent


@pytest.fixture
def setup():
    player1 = Player("Alice")
    player2 = Player("Bob")
    player1.mage = Alchemist()
    player2.mage = Alchemist()
    engine = Engine(
        players=[player1, player2],
        mages=[],
        artifacts=[],
        monuments=[],
        places_of_power=[],
        objects=[],
        scrolls=[]
    )
    engine.state.engine = engine
    dragon = BoneDragon()
    player1.board.append(dragon)
    player1.resources.add(Resource.DEATH, 3)
    player1.resources.add(Resource.ELAN, 1)
    player2.resources.add(Resource.LIFE, 4)
    return engine, player1, player2, dragon


def test_attaque_paye_life(setup):
    """Le joueur attaqué paie 2 LIFE"""
    engine, player1, player2, dragon = setup
    with patch('builtins.input', side_effect=['2', '1']):
        # 2 = pas d'esquive DEATH, 1 = payer les dégâts
        engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 2


def test_attaque_esquive_death(setup):
    """Le joueur attaqué esquive en payant 1 DEATH"""
    engine, player1, player2, dragon = setup
    player2.resources.add(Resource.DEATH, 1)
    ability = dragon.get_abilities()[0]
    with patch('builtins.input', return_value='1'):
        ability.execute(engine.state, player1)
    assert player2.resources.resources[Resource.DEATH] == 0
    assert player2.resources.resources[Resource.LIFE] == 4


def test_attaque_life_manquant(setup):
    """Le joueur paie 1 LIFE + 2 ressources pour le LIFE manquant"""
    engine, player1, player2, dragon = setup
    player2.resources.remove(Resource.LIFE, 3)  # il ne lui reste que 1 LIFE
    player2.resources.add(Resource.ELAN, 2)
    with patch('builtins.input', side_effect=['2', '1', '1', '1']):
        # 2 = pas d'esquive, 1 = payer, puis 2x choisir ELAN
        engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 0
    assert player2.resources.resources[Resource.ELAN] == 0


def test_grande_muraille_esquive(setup):
    """La Grande Muraille annule l'attaque"""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    player2.board.append(wall)
    player2.resources.add(Resource.ELAN, 1)
    with patch('builtins.input', side_effect=['2', '1']):
        # 2 = utiliser une carte, 1 = activer la Grande Muraille
        engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 4
    assert player2.resources.resources[Resource.ELAN] == 0
    assert wall.is_tapped == False


def test_grande_muraille_pas_elan(setup):
    """La Grande Muraille ne peut pas s'activer sans ELAN"""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    player2.board.append(wall)
    with patch('builtins.input', side_effect=['1']):
        engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 2
    assert wall.is_tapped == False