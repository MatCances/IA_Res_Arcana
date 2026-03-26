from cards.base_card import Card
from utils.constant import Resource, GameEvent, CardType
from game.action import Action
from game.ability import Ability
from cli.input_handler import choose_resource, choose_card

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
            resource = choose_resource(choices)
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
            
            print(f"\n[Réaction] {owner.name} : voulez-vous activer l'Autel Abyssal ? (+1 GOLD, s'engage)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix: "))
                except ValueError:
                    pass
            if choice == 1:
                self.resources_on.add(Resource.GOLD, 1)
                self.tap()
                print(f"[Réaction] {self.name} : +1 GOLD posé sur la carte (engagée)")
    
    def score(self, state, player):
        return 1 + self.resources_on.resources[Resource.GOLD]


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
            resource = choose_resource(player.resources.available())
            player.resources.remove(resource, 1)

            if not player.board:
                print("Vous n'avez aucune carte sur le plateau.")
                return
            
            print("Choisissez une carte sur laquelle poser la ressource :")
            card = choose_card(player.board)
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
        resource = choose_resource([Resource.ELAN, Resource.DEATH])
        player.resources.add(resource, 1)
    
    def get_abilities(self):
        def effect(state, player):
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée sur votre plateau.")
                return
            player.resources.remove(Resource.GOLD, 1)
            print("Choisissez une carte à désengager :")
            card = choose_card(tapped)
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
            resource = choose_resource(player.resources.available())
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

        for i in range(3):
            resource = choose_resource(choices)
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
            resource = choose_resource(player.resources.available())
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
        super().__init__("Great Wall")
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            if source_player != owner:
                return
            if not owner.resources.has(Resource.ELAN, 1):
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous activer la Grande Muraille ? (1 ELAN, s'engage)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                owner.resources.remove(Resource.ELAN, 1)
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] Grande Muraille : attaque annulée !")
    
    def score(self, state, player):
        return 2


class Oracle(Monument):
    def __init__(self):
        super().__init__("Oracle")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez la pioche à consulter :")
            print("1 - Votre pioche")
            print("2 - La pioche des monuments")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            
            if choice == 1:
                deck = player.deck
            else:
                deck = state.monuments
            
            if not deck:
                print("La pioche est vide !")
                return
            
            # piocher 3 cartes
            drawn = deck[:3]
            del deck[:3]

            # réordonner au choix du joueur
            print("Cartes piochées, réordonnez-les :")
            reordered = []
            remaining = drawn[:]
            while remaining:
                for i, card in enumerate(remaining):
                    print(f"{i+1} - {card.name}")
                pick = 0
                while pick < 1 or pick > len(remaining):
                    try:
                        pick = int(input(f"Choisissez la carte à placer en position {len(reordered) + 1} : "))
                    except ValueError:
                        pass
                reordered.append(remaining.pop(pick - 1))
            
            # reposer sur la pioche
            deck[:0] = reordered
            print("Cartes replacées sur la pioche dans le nouvel ordre.")
            self.tap()
        
        return [Ability("Consulter et réordonner le top 3 d'une pioche", cost={}, effect=effect)]
    
    def score(self, state, player):
        return 2


class Temple(Monument):
    def __init__(self):
        super().__init__("Temple")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.LIFE, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            if source_player != owner:
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous activer le Temple pour esquiver ?")
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
                print(f"[Réaction] Temple : attaque annulée !")
    
    def score(self, state, player):
        return 2


class ImpiousCathedral(Monument):
    def __init__(self):
        super().__init__("Impious Cathedral")
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.VICTORY_CHECK and not self.is_tapped:
            owner = next((p for p in state.players if self in p.board), None)
            if owner is None:
                return
            demons = [card for card in owner.board if hasattr(card, 'card_type') and card.card_type in {CardType.DEMON, CardType.ILLUSIONIST} and not card.is_tapped]
            if not demons:
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous activer la Cathédrale Impie ? (s'engage + engage un démon pour +1 point)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                print("Choisissez un démon à engager :")
                demon = choose_card(demons)
                self.tap()
                demon.tap()
                owner.points += 1
                print(f"[Réaction] Cathédrale Impie : +1 point !")
    
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
            
            print(f"\n[Réaction] {owner.name} : voulez-vous activer la Statue Sacrée ? (3 GOLD → +3 points, s'engage)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                owner.resources.remove(Resource.GOLD, 3)
                print("owner.points: (avant)", owner.points)
                owner.bonus_points += 3
                print("OUUUUAIII ca passe par le on_event de sacred statue")
                print("owner.points: (apres)", owner.points)
                self.tap()
                print(f"[Réaction] Statue Sacrée : -3 GOLD, +3 points !")
    
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