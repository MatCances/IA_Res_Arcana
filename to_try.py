from cards.scrolls import Recovery
from cards.artifacts import Phoenix, PlanarShadow, BoneDragon, Automate
from game.game_state import GameState
from game.player import Player
from game.engine import Engine
from cards.mages import Artificer, Draconist
from utils.constant import Resource


player1 = Player("Kanss")
player2 = Player("Zib")
player1.mage = Draconist()
player2.mage = Artificer()
dragon = BoneDragon()
automate = Automate()
engine = Engine(players=[player1, player2], mages=[], artifacts=[], monuments=[], places_of_power=[], objects=[], scrolls=[])
engine.state.engine = engine
engine.state.places_of_power = []
engine.state.monuments_visible = []
player1.hand.append(dragon)
player1.hand.append(automate)

player1.resources.add(Resource.DEATH, 2)
player1.resources.add(Resource.LIFE, 1)
player1.resources.add(Resource.GOLD, 1)
player1.resources.add(Resource.ELAN, 1)
player1.resources.add(Resource.CALM, 1)

print(f"player1.resources: {player1.resources}")
print(f"player1.can_buy BoneDragon (sans draconniste) ? {player1.can_buy(card=dragon)}")

player1.board.append(player1.mage)
player1.board.append(Artificer())

while True:
    print(f"\n+===== MANCHE {engine.state.turn} =====")
    engine.collect_phase()
    engine.action_phase()
    if engine.game_over:
        break
    engine.untap_all()
    winner = engine.victory_check()
    if winner:
        break
    engine.state.turn += 1
