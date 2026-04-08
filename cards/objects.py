from cards.base_card import Card
from utils.constant import Resource, GameEvent, CardType
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
        resource = player.choose_resource([Resource.CALM, Resource.ELAN], state)
        player.resources.add(resource, 1)


class DeathLife(Obj):
    def __init__(self):
        super().__init__("Death / Life")
    
    def collect_base(self, state, player):
        print(f"{player.name}, choisissez une ressource à collecter (Death / Life) :")
        resource = player.choose_resource([Resource.DEATH, Resource.LIFE], state)
        player.resources.add(resource, 1)


class Reanimate(Obj):
    def __init__(self):
        super().__init__("Reanimate")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez la ressource à payer: ")
            resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}), state)
            player.resources.remove(resource, 1)
            
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée.")
                self.tap()
                return
            
            print("Choisissez une carte à désengager: ")
            card = player.choose_card(tapped, state)
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
                resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}), state)
                player.resources.remove(resource, 1)
            player.resources.add(Resource.GOLD, 2)
            self.tap()

        abilities = [Ability("4 ressources au choix pour 2 GOLD", cost={Resource.ANY: 4}, effect=effect)]
        return abilities


class Protection(Obj):
    def __init__(self):
        super().__init__("Protection")
        self.has_attack_reaction = True
        self.attack_reaction_requires_untapped = True
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : engager {self.name} ?", state):
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
                card = player.choose_card(player.hand, state)
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
            
            resource = player.choose_resource(player.resources.available(), state)
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
                resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}), state)
                player.resources.remove(resource, 1)
            
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]
            print("Choisissez 3 ressources à recevoir :")
            for _ in range(3):
                resource = player.choose_resource(choices, state)
                player.resources.add(resource, 1)
            
            self.tap()
        
        return [Ability("3 ressources pour 3 ressources (sauf gold et pearl)", cost={Resource.ANY: 3}, effect=effect)]


class Illusion(Obj):
    def __init__(self):
        super().__init__("Illusion")
        self.card_type = CardType.ILLUSIONIST


class Calcination(Obj):
    def __init__(self):
        super().__init__("Calcination")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 3 ressources à payer :")
            for _ in range(3):
                resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}), state)
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
            if not state.scrolls:
                print("Aucun parchemin disponible.")
                return
            
            print("Choisissez une ressource à payer :")
            resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}), state)
            player.resources.remove(resource, 1)

            print("Choisissez un parchemin :")
            scroll = player.choose_card(state.scrolls, state)
            
            state.scrolls.remove(scroll)
            player.board.append(scroll)
            print(f"{player.name} prend {scroll.name}")
            self.tap()
        
        return [Ability("1 ressource pour prendre un parchemin", cost={Resource.ANY: 1}, effect=effect)]

ALL_OBJECTS = [CalmElan(),
               DeathLife(),
               Reanimate(),
               Alchemy(),
               Protection(),
               Divination(),
               Research(),
               Transmutation(),
               Calcination(),
               Inscription(),
               Illusion()]
