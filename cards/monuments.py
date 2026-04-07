from cards.base_card import Card
from utils.constant import Resource, GameEvent, CardType
from game.action import Action
from game.ability import Ability

class Monument(Card):
    def __init__(self, name):
        cost = {Resource.GOLD: 4}
        super().__init__(name, cost)
    
    def on_buy(self, state, player):
        """Effet déclenché une seule fois à l'achat.
        Utile pour l'obelisque"""
        pass


class Obelisc(Monument):
    def __init__(self):
        name = "Obelisc"
        super().__init__(name)
    
    def on_buy(self, state, player):
        print(f"{player.name}, choisissez 6 ressources :")
        excluded = {Resource.GOLD, Resource.PEARL}
        choices = [r for r in Resource.real() if r not in excluded]
        for _ in range(6):
            resource = player.choose_resource(choices)
            player.resources.add(resource, 1)
    
    def score(self, state, player):
        return 1


class AbyssalAltar(Monument):
    def __init__(self):
        name = "Abyssal Altar"
        super().__init__(name)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.DEATH, 2)
            player.resources.add(Resource.PEARL, 1)
            self.tap()
        
        abilities = [Ability("2 DEATH pour 1 PEARL", cost={Resource.DEATH: 2}, effect=effect)]
        return abilities
    
    def score(self, state, player):
        return 1


class ForgottenDomain(Monument):
    def __init__(self):
        name = "Forgotten Domain"
        super().__init__(name)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.BUY_MONUMENT and not self.is_tapped:

            # Propritétaire de la carte
            for p in state.players:
                if self in p.board:
                    owner = p
                    break
            
            # Si c'est un autre joueur qui achète le monument: pass
            if source_player != owner:
                return
            
            # Si le monument qu'on achète est lui meme: pass
            if kwargs.get("monument") == self:
                return
            
            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : engager {self.name} ? (+1 GOLD sur la carte)"):
        
                self.resources_on.add(Resource.GOLD, 1)
                self.tap()
                print(f"[Réaction] {self.name} : +1 GOLD posé sur la carte (engagée)")
    
    def score(self, state, player):
        return 1 + self.resources_on.get_amount(Resource.GOLD)


class Library(Monument):
    def __init__(self):
        super().__init__("Library")
    
    def get_abilities(self):
        def effect(state, player):
            if not player.deck:
                print(f"{player.name} n'a plus de cartes dans sa pioche.")
                return
            card = player.deck.pop(0)
            player.hand.append(card)
            print(f"{player.name} pioche {card.name}")
            self.tap()
        
        return [Ability("Piocher une carte", cost={}, effect=effect)]
    
    def score(self, state, player):
        return 1


class Laboratory(Monument):
    def __init__(self):
        super().__init__("Laboratory")
    
    def get_abilities(self):
        def effect(state, player):
            if not player.resources.available():
                print("Vous n'avez aucune ressource à payer.")
                return
            
            print("Choisissez une ressource à payer :")
            resource = player.choose_resource(player.resources.available())
            player.resources.remove(resource, 1)

            if not player.board:
                print("Vous n'avez aucune carte sur le plateau.")
                return
            
            print("Choisissez une carte sur laquelle poser la ressource :")
            card = player.choose_card(player.board)
            card.resources_on.add(resource, 1)
            print(f"{resource.value} posé sur {card.name}")
            self.tap()
        
        return [Ability("Payer 1 ressource pour la poser sur une carte", cost={Resource.ANY: 1}, effect=effect)]
    
    def score(self, state, player):
        return 1


class Pyramid(Monument):
    def __init__(self):
        super().__init__("Pyramide")
    
    def score(self, state, player):
        return 3


class DemonicWorkshop(Monument):
    def __init__(self):
        super().__init__("Atelier Démoniaque")
    
    def collect_base(self, state, player):
        print(f"{player.name}, choisissez une ressource à collecter (Elan / Death) :")
        resource = player.choose_resource([Resource.ELAN, Resource.DEATH])
        player.resources.add(resource, 1)
    
    def get_abilities(self):
        def effect(state, player):
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée sur votre plateau.")
                return
            player.resources.remove(Resource.GOLD, 1)
            print("Choisissez une carte à désengager :")
            card = player.choose_card(tapped)
            card.untap()
            print(f"{card.name} est désengagée.")
            self.tap()
        
        return [Ability("Désengager une carte du plateau pour 1 GOLD", cost={Resource.GOLD: 1}, effect=effect)]
    
    def score(self, state, player):
        return 1


class SolomonsMine(Monument):
    def __init__(self):
        super().__init__("Solomon's Mine")
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.add(Resource.GOLD, 1)
            self.tap()
            print(f"{player.name} gagne 1 GOLD")
        
        return [Ability("Produire 1 GOLD", cost={}, effect=effect)]
    
    def score(self, state, player):
        return 1


class Mausoleum(Monument):
    def __init__(self):
        super().__init__("Mausoleum")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez une ressource à payer :")
            resource = player.choose_resource(player.resources.available())
            player.resources.remove(resource, 1)
            self.resources_on.add(Resource.DEATH, 1)
            print(f"1 DEATH posé sur le Mausolée.")
        
        return [Ability("1 ressource pour 1 DEATH sur la carte", cost={Resource.ANY: 1}, effect=effect)]
    
    def score(self, state, player):
        return 2


class HangingGarden(Monument):
    def __init__(self):
        super().__init__("Hanging Garden")

    def collect_base(self, state, player):
        excluded = {Resource.GOLD, Resource.PEARL}
        choices = [r for r in Resource.real() if r not in excluded]
        print(f"{self.name} : choisissez 3 ressource à collecter :")

        for _ in range(3):
            resource = player.choose_resource(choices)
            player.resources.add(resource, 1)


class SolomonsTemple(Monument):
    def __init__(self):
        super().__init__("Solomon's Temple")
    
    def get_abilities(self):
        def effect(state, player):
            cost = {Resource.ELAN: 1, Resource.CALM: 1, Resource.DEATH: 1, Resource.LIFE: 1}
            for resource, _ in cost.items():
                player.resources.remove(resource, 1)
            self.resources_on.add(Resource.PEARL, 1)
            print(f"1 PEARL posé sur le Temple de Salomon.")
        
        return [Ability("1 ELAN + 1 CALM + 1 DEATH + 1 LIFE pour 1 PEARL sur la carte",
                        cost={Resource.ELAN: 1, Resource.CALM: 1, Resource.DEATH: 1, Resource.LIFE: 1},
                        effect=effect)]
    
    def score(self, state, player):
        return 2


class Colossus(Monument):
    def __init__(self):
        super().__init__("Colossus")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez une ressource à payer :")
            resource = player.choose_resource(player.resources.available())
            player.resources.remove(resource, 1)
            self.resources_on.add(Resource.GOLD, 1)
            print(f"1 GOLD posé sur le Colosse.")
            self.tap()
        
        return [Ability("1 ressource pour 1 GOLD sur la carte", cost={Resource.ANY: 1}, effect=effect)]
    
    def score(self, state, player):
        return 2


class Pantheon(Monument):
    def __init__(self):
        super().__init__("Pantheon")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.ELAN, 1)
    
    def get_abilities(self):
        def effect(state, player):
            for p in state.players:
                p.resources.add(Resource.ELAN, 1)
                print(f"{p.name} gagne 1 ELAN")
            self.tap()
        
        return [Ability("Tout le monde gagne 1 ELAN", cost={}, effect=effect)]
    
    def score(self, state, player):
        return 2


class GreatWall(Monument):
    def __init__(self):
        super().__init__("Grande Muraille")
        self.has_attack_reaction = True
        self.attack_reaction_requires_untapped = False
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK:
            owner = next(p for p in state.players if self in p.board)
            if not owner.resources.has(Resource.ELAN, 1):
                return
            
            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : utiliser {self.name} ? (1 ELAN)"):
                owner.resources.remove(Resource.ELAN, 1)
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")
    
    def score(self, state, player):
        return 2


class Oracle(Monument):
    def __init__(self):
        super().__init__("Oracle")
    
    def get_abilities(self):
        def effect(state, player):
            options = ["Votre pioche", "La pioche des monuments"]
            choice = player.choose_option(options)
            if choice == 0:
                deck = player.deck
            else:
                deck = state.monuments_deck

            if not deck:
                print("La pioche est vide !")
                return

            # piocher 3 cartes
            # Ceci ne renvoie que 2 cartes si seulement 2 cartes sont dans la pioche
            drawn = deck[:3]
            del deck[:3]

            # réordonner au choix du joueur
            reordered = []
            remaining = drawn[:]
            while remaining:
                print(f"Choisissez la carte à placer en position {len(reordered) + 1} :")
                card = player.choose_card(remaining)
                reordered.append(card)
                remaining.remove(card)

            # reposer sur la pioche
            deck[:0] = reordered
            print("Cartes replacées sur la pioche dans le nouvel ordre.")
            self.tap()
        
        return [Ability(f"Engager: piocher 3 cartes, les réordonner, les replacer sur la pioche",
                        cost={},
                        effect=effect)]
    
    def score(self, state, player):
        return 2


class Temple(Monument):
    def __init__(self):
        super().__init__("Temple")
        self.has_attack_reaction = True
        self.attack_reaction_requires_untapped = True
    
    def collect_base(self, state, player):
        player.resources.add(Resource.LIFE, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)

            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : engager {self.name} ?"):
                self.tap()
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")
    
    def score(self, state, player):
        return 2


class ImpiousCathedral(Monument):
    def __init__(self):
        super().__init__("Cathédrale Impie")
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.VICTORY_CHECK and not self.is_tapped:
            owner = next((p for p in state.players if self in p.board), None)
            if owner is None:
                return
            demons = [c for c in owner.board
                      if c.card_type in {CardType.DEMON, CardType.ILLUSIONIST}
                      and not c.is_tapped]
            if not demons:
                return
            
            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : activer {self.name} ? (s'engage + engage un démon, +1 point)"):
                print("Choisissez un démon à engager :")
                demon = owner.choose_card(demons)
                self.tap()
                demon.tap()
                owner.bonus_points += 1
                print(f"[Réaction] {self.name} : +1 point !")
    
    def score(self, state, player):
        return 2


class SacredStatue(Monument):
    def __init__(self):
        super().__init__("Statue Sacrée")
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.VICTORY_CHECK and not self.is_tapped:
            owner = next((p for p in state.players if self in p.board), None)
            if owner is None:
                return
            if not owner.resources.has(Resource.GOLD, 3):
                return
            
            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : activer {self.name} ? (3 GOLD → +3 points, s'engage)"):
                owner.resources.remove(Resource.GOLD, 3)
                owner.bonus_points += 3
                self.tap()
                print(f"[Réaction] {self.name} : -3 GOLD, +3 points !")
    
    def score(self, state, player):
        return 1

ALL_MONUMENTS = [Obelisc(),
                 AbyssalAltar(),
                 ForgottenDomain(),
                 Library(),
                 Laboratory(),
                 Pyramid(),
                 DemonicWorkshop(),
                 SolomonsMine(),
                 Mausoleum(),
                 HangingGarden(),
                 SolomonsTemple(),
                 Colossus(),
                 Pantheon(),
                 GreatWall(),
                 Oracle(),
                 Temple(),
                 ImpiousCathedral(),
                 SacredStatue()]