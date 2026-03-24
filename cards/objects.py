from cards.base_card import Card
from utils.constant import Resource, GameEvent
from cli.input_handler import choose_resource, choose_card
from game.action import Action
from game.ability import Ability

class Obj(Card):
    def __init__(self, name):
        super().__init__(name, cost={})


class CalmElan(Obj):
    def __init__(self):
        super().__init__("Calm / Elan")
    
    def collect_base(self, state, player):
        print(f"{player.name}, choisissez une ressource à collecter (Calm / Elan) :")
        resource = choose_resource([Resource.CALM, Resource.ELAN])
        player.resources.add(resource, 1)


class DeathLife(Obj):
    def __init__(self):
        super().__init__("Death / Life")
    
    def collect_base(self, state, player):
        print(f"{player.name}, choisissez une ressource à collecter (Death / Life) :")
        resource = choose_resource([Resource.DEATH, Resource.LIFE])
        player.resources.add(resource, 1)


class Reanimate(Obj):
    def __init__(self):
        super().__init__("Reanimate")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez la ressource à payer: ")
            resource = choose_resource(player.resources.available(excluded={Resource.ANY, Resource.PEARL}))
            player.resources.remove(resource, 1)
            

            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée.")
                self.tap()
                return
            
            print("Choisissez une carte à désengager: ")
            card = choose_card(tapped)
            card.untap()
            self.tap()

        abilities = [Ability("1 ressource au choix pour désengager une carte", cost={Resource.ANY: 1}, effect=effect)]
        return abilities


class Alchemy(Obj):
    def __init__(self):
        super().__init__("Alchemy")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 4 ressources à payer :")
            for _ in range(4):
                resource = choose_resource(player.resources.available(excluded={Resource.ANY, Resource.PEARL}))
                player.resources.remove(resource, 1)
            player.resources.add(Resource.GOLD, 2)
            self.tap()

        abilities = [Ability("4 ressources au choix pour 2 GOLD", cost={Resource.ANY: 4}, effect=effect)]
        return abilities


class Protection(Obj):
    def __init__(self):
        super().__init__("Protection")
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next((p for p in state.players if self in p.board), None)
            if owner is None or source_player != owner:
                return
            
            print(f"\n[Réaction] {owner.name} : voulez-vous activer {self.name} ? (annule l'attaque, s'engage)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                self.tap()
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")


class Divination(Obj):
    def __init__(self):
        super().__init__("Divination")
    
    def get_abilities(self):
        def effect(state, player):
            # piocher jusqu'à 3 cartes
            nb = min(3, len(player.deck))
            if nb == 0:
                print(f"{player.name} n'a plus de cartes dans sa pioche.")
                return
            
            drawn = [player.deck.pop(0) for _ in range(nb)]
            for card in drawn:
                player.hand.append(card)
                print(f"{player.name} pioche {card.name}")
            
            # défausser autant qu'on a pioché
            print(f"Choisissez {nb} carte(s) à défausser :")
            for _ in range(nb):
                card = choose_card(player.hand)
                player.hand.remove(card)
                player.discard.append(card)
                print(f"{player.name} défausse {card.name}")
            
            self.tap()
        
        return [Ability("Piocher 3 cartes puis défausser 3 cartes", cost={}, effect=effect)]


class Research(Obj):
    def __init__(self):
        super().__init__("Recherche")
    
    def get_abilities(self):
        def effect(state, player):
            if not player.deck:
                print(f"{player.name} n'a plus de cartes dans sa pioche.")
                return
            
            resource = choose_resource(player.resources.available())
            player.resources.remove(resource, 1)
            
            card = player.deck.pop(0)
            player.hand.append(card)
            print(f"{player.name} pioche {card.name}")
            self.tap()
        
        return [Ability("1 ressource au choix pour piocher une carte", cost={Resource.ANY: 1}, effect=effect)]


class Transmutation(Obj):
    def __init__(self):
        super().__init__("Transmutation")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 3 ressources à payer :")
            for _ in range(3):
                resource = choose_resource(player.resources.available(excluded={Resource.PEARL}))
                player.resources.remove(resource, 1)
            
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]
            print("Choisissez 3 ressources à recevoir :")
            for _ in range(3):
                resource = choose_resource(choices)
                player.resources.add(resource, 1)
            
            self.tap()
        
        return [Ability("3 ressources pour 3 ressources (sauf gold et pearl)", cost={Resource.ANY: 3}, effect=effect)]


class Calcination(Obj):
    def __init__(self):
        super().__init__("Calcination")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 3 ressources à payer :")
            for _ in range(3):
                resource = choose_resource(player.resources.available(excluded={Resource.PEARL}))
                player.resources.remove(resource, 1)
            
            player.resources.add(Resource.PEARL, 1)
            print(f"{player.name} obtient 1 PEARL")
            self.tap()
        
        return [Ability("3 ressources pour 1 PEARL", cost={Resource.ANY: 3}, effect=effect)]


class Inscription(Obj):
    def __init__(self):
        super().__init__("Inscription")
    
    def get_abilities(self):
        def effect(state, player):
            if not state.engine.available_scrolls:
                print("Aucun parchemin disponible.")
                return
            
            print("Choisissez un parchemin :")
            scroll = choose_card(state.engine.available_scrolls)
            
            print("Choisissez une ressource à payer :")
            resource = choose_resource(player.resources.available(excluded={Resource.PEARL}))
            player.resources.remove(resource, 1)
            
            state.engine.available_scrolls.remove(scroll)
            player.board.append(scroll)
            print(f"{player.name} prend {scroll.name}")
            self.tap()
        
        return [Ability("1 ressource pour prendre un parchemin", cost={Resource.ANY: 1}, effect=effect)]

ALL_OBJECTS = [CalmElan(),
               DeathLife(),
               Reanimate(),
               Alchemy(),
               Shield(),
               Divination(),
               Research(),
               Transmutation(),
               Calcination(),
               Inscription()]
