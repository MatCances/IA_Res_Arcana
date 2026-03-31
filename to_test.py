from cards.scrolls import Recovery
from cards.artifacts import Phoenix, PlanarShadow
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from cards.mages import Artificer
from utils.constant import Resource


player = Player("Alice")
player.mage = Artificer()
engine = Engine(players=[player], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
engine.state.engine = engine
player.hand.append(Phoenix())

player.resources.add(Resource.ELAN, 2)
player.resources.add(Resource.LIFE, 1)

print(f"player.resources: {player.resources}")
print(f"player.can_buy Phoenix (sans artificier) ? {player.can_buy(card=Phoenix())}")

player.board.append(player.mage)
print(f"player.resources: {player.resources}")
print(f"player.can_buy Phoenix (avec artificier) ? {player.can_buy(card=Phoenix())}")

player.resources.remove(Resource.LIFE, 1)
player.resources.add(Resource.ELAN, 1)
print(f"player.resources: {player.resources}")
print(f"player.can_buy Phoenix (avec artificier) ? {player.can_buy(card=Phoenix())}")

player.resources.add(Resource.LIFE, 1)
player.resources.add(Resource.ELAN, 1)
print(f"player.resources: {player.resources}")
print(f"player.can_buy Phoenix (avec artificier) ? {player.can_buy(card=Phoenix())}")