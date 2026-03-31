from cards.scrolls import Recovery
from cards.artifacts import Phoenix, PlanarShadow, BoneDragon
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from cards.mages import Artificer, Draconist
from utils.constant import Resource


player = Player("Alice")
player.mage = Draconist()
dragon = BoneDragon()
engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
engine.state.engine = engine
engine.state.places_of_power = []
engine.state.monuments_visible = []
player.hand.append(dragon)

player.resources.add(Resource.DEATH, 2)
player.resources.add(Resource.LIFE, 1)

print(f"player.resources: {player.resources}")
print(f"player.can_buy BoneDragon (sans draconniste) ? {player.can_buy(card=dragon)}")

player.board.append(player.mage)
player.board.append(Artificer())

while True:
    engine.action_phase()
    engine.untap_all()
