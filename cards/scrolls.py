from cards.base_card import Card
from utils.constant import Resource, GameEvent
from game.ability import Ability
from cli.input_handler import choose_card

class Scroll(Card):
    def __init__(self, name, cost):
        super().__init__(name, cost=cost)


class Vitality(Scroll):
    def __init__(self):
        super().__init__("Vitalité", cost={Resource.LIFE: 1})
    
    def get_abilities(self):
        def effect(state, player):
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée sur votre plateau.")
                return
            
            print("Choisissez une carte à désengager :")
            card = choose_card(tapped)
            card.untap()
            print(f"{card.name} est désengagée.")
            
            player.board.remove(self)
            state.engine.available_scrolls.append(self)
        
        return [Ability("Désengager une carte du plateau", cost={Resource.ELAN: 2}, effect=effect)]
    

ALL_SCROLLS = [Vitality()]