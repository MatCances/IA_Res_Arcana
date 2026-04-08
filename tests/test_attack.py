import pytest
from unittest.mock import patch
from cards.artifacts import BoneDragon
from cards.monuments import GreatWall
from cards.scrolls import Shield
from cards.objects import Protection
from game.engine import Engine
from game.human_player import HumanPlayer
from cards.mages import Alchemist
from utils.constant import Resource, GameEvent


@pytest.fixture
def setup():
    player1 = HumanPlayer("Alice")
    player2 = HumanPlayer("Bob")
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


# --- Paiement en LIFE ---

def test_attaque_paye_life(setup):
    """Le joueur attaqué paie 2 LIFE (aucune réaction disponible)."""
    engine, player1, player2, dragon = setup
    engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 2


def test_attaque_life_manquant_paye_ressources(setup):
    """1 LIFE dispo pour dommage 2 : paie 1 LIFE + 2 ressources pour le LIFE manquant."""
    engine, player1, player2, dragon = setup
    player2.resources.remove(Resource.LIFE, 3)  # reste 1 LIFE
    player2.resources.add(Resource.ELAN, 2)
    with patch.object(player2, 'choose_resource', side_effect=[Resource.ELAN, Resource.ELAN]):
        engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 0
    assert player2.resources.resources[Resource.ELAN] == 0


def test_attaque_aucune_ressource_ne_fait_rien(setup):
    """0 LIFE et aucune ressource : rien ne se passe, pas d'erreur."""
    engine, player1, player2, dragon = setup
    player2.resources.remove(Resource.LIFE, 4)
    engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 0
    assert player2.resources.total == 0


def test_attaque_life_partiel_sans_ressources(setup):
    """1 LIFE pour dommage 2, aucune autre ressource : perd juste 1 LIFE."""
    engine, player1, player2, dragon = setup
    player2.resources.remove(Resource.LIFE, 3)  # reste 1 LIFE, rien d'autre
    engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 0
    assert player2.resources.total == 0


# --- Réaction : Grande Muraille ---

def test_grande_muraille_esquive(setup):
    """La Grande Muraille annule l'attaque en payant 1 ELAN."""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    player2.board.append(wall)
    player2.resources.add(Resource.ELAN, 1)
    with patch.object(player2, 'choose_option', return_value=1):
        with patch.object(player2, 'choose_yes_no', return_value=True):
            engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 4
    assert player2.resources.resources[Resource.ELAN] == 0


def test_grande_muraille_joueur_choisit_subir(setup):
    """Le joueur choisit de subir les dégâts plutôt qu'utiliser la Grande Muraille."""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    player2.board.append(wall)
    player2.resources.add(Resource.ELAN, 1)
    with patch.object(player2, 'choose_option', return_value=0):
        engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 2
    assert player2.resources.resources[Resource.ELAN] == 1


def test_grande_muraille_pas_elan_ne_peut_pas_annuler(setup):
    """Sans ELAN la Grande Muraille est proposée mais ne peut pas annuler."""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    player2.board.append(wall)
    with patch.object(player2, 'choose_option', return_value=1):
        with patch.object(player2, 'choose_yes_no', return_value=True):
            engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 2


# --- Plusieurs cartes de réaction ---

def test_plusieurs_reactions_joueur_choisit(setup):
    """Avec 2 cartes de réaction, le joueur choisit laquelle utiliser."""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    shield = Shield()
    player2.board.append(wall)
    player2.board.append(shield)
    player2.resources.add(Resource.ELAN, 1)
    # options: 0=subir, 1=Grande Muraille, 2=Bouclier → choisit Bouclier
    with patch.object(player2, 'choose_option', return_value=2):
        with patch.object(player2, 'choose_yes_no', return_value=True):
            engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 4
    assert shield not in player2.board  # Bouclier consommé


# --- Flags attack_reaction_requires_untapped ---

def test_carte_requires_untapped_exclue_si_engagee(setup):
    """attack_reaction_requires_untapped=True : carte engagée non proposée."""
    engine, player1, player2, dragon = setup
    protection = Protection()
    protection.tap()
    player2.board.append(protection)
    with patch.object(player2, 'choose_option') as mock_choice:
        engine.resolve_attack(player2, damage=2)
    mock_choice.assert_not_called()
    assert player2.resources.resources[Resource.LIFE] == 2


def test_carte_requires_untapped_false_proposee_meme_engagee(setup):
    """attack_reaction_requires_untapped=False : carte proposée même engagée."""
    engine, player1, player2, dragon = setup
    wall = GreatWall()
    wall.tap()
    player2.board.append(wall)
    player2.resources.add(Resource.ELAN, 1)
    with patch.object(player2, 'choose_option', return_value=1):
        with patch.object(player2, 'choose_yes_no', return_value=True):
            engine.resolve_attack(player2, damage=2)
    assert player2.resources.resources[Resource.LIFE] == 4


# --- Esquive via effet d'une carte attaquante (alternative DEATH) ---

def test_attaque_esquive_death(setup):
    """Le dragon propose d'esquiver en payant 1 DEATH."""
    engine, player1, player2, dragon = setup
    player2.resources.add(Resource.DEATH, 1)
    ability = dragon.get_abilities()[0]
    with patch('builtins.input', return_value='1'):
        ability.execute(engine.state, player1)
    assert player2.resources.resources[Resource.DEATH] == 0
    assert player2.resources.resources[Resource.LIFE] == 4
