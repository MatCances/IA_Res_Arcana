from cards.base_card import Card
from utils.constant import Resource, CardType
from game.ability import Ability
from cli.input_handler import choose_resource, choose_card


class Artifact(Card):
    def __init__(self, name, cost, card_type=CardType.NONE):
        super().__init__(name, cost=cost, card_type=card_type)
    
    def play(self, state, player):
        """Vérifie le coût et applique l'ability"""
        if not player.can_buy(self):
            print(f" ! Pas assez de ressources pour jouer {self.name} !")
            return False
        # retirer le coût
        for r, amount in self.cost.items():
            player.resources.remove(r, amount)

        # Ajoute la carte au plateau du joueur et la retire de sa main
        player.board.append(self)
        player.hand.remove(self)
        return True
    
    def discard(self, state, player):
        player.hand.remove(self)
        player.discard.append(self)
        print(f"{player.name} défausse {self.name}")

        print("Choisissez une option :")
        print("1 - Recevoir 2 ressources")
        print("2 - Recevoir 1 GOLD")
        choix = 0
        while choix not in [1, 2]:
            try:
                choix = int(input("Choix (1 ou 2) : "))
            except ValueError:
                print("  ! Merci de taper un chiffre valide !")

        if choix == 2:
            player.resources.add(Resource.GOLD, 1)
            print("Vous recevez 1 GOLD")
        else:
            print("Choisissez 2 ressources :")
            for _ in range(2):
                resource = choose_resource([r for r in Resource.real() if r != Resource.PEARL])
                player.resources.add(resource, 1)
            print("Vous recevez 2 ressources")

class Phoenix(Artifact):
    def __init__(self):
        name = "Phoenix"
        cost = {Resource.ELAN: 3, Resource.LIFE: 1}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.add(Resource.GOLD, 1)
            self.tap()

        abilities = [Ability("Obtiens 1 GOLD", cost={}, effect=effect)]
        return abilities

class Prism(Artifact):
    def __init__(self):
        name = "Prism"
        cost = {}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect1(state, player):
            print("Choisissez 1 ressource à payer :")
            resource = choose_resource(player.resources.available(excluded={Resource.PEARL}))
            player.resources.remove(resource, 1)
            print("Choisissez 2 ressources à recevoir :")
            for _ in range(2):
                r = choose_resource([r for r in Resource.real() if r != Resource.PEARL])
                player.resources.add(r, 1)
            self.tap()
        
        def effect2(state, player):
            print("Choisissez la ressource source :")
            source = choose_resource(player.resources.available(excluded={Resource.PEARL}))
            amount = player.resources.resources[source]
            if amount == 0:
                print(f"Vous n'avez pas de {source.value}.")
                return
            print("Choisissez la ressource cible :")
            cible = choose_resource([r for r in Resource.real() if r != Resource.PEARL])
            player.resources.remove(source, amount)
            player.resources.add(cible, amount)
            print(f"{player.name} convertit {amount} {source.value} en {cible.value}.")
            self.tap()
        
        abilities = [Ability("1 ressource contre 2 ressources", cost={Resource.ANY: 1}, effect=effect1),
                     Ability("Convertit toutes les ressources d'un type", cost={Resource.ANY: 1}, effect=effect2)]
        return abilities


class LightFlask(Artifact):
    def __init__(self):
        name = "Light flask"
        cost = {}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.DEATH, 1)
            player.resources.add(Resource.LIFE, 1)
            player.resources.add(Resource.ELAN, 1)
            self.tap()

        abilities = [Ability("1 DEATH pour 1 LIFE + 1 ELAN", cost={Resource.DEATH: 1}, effect=effect)]
        return abilities


class PlanarShadow(Artifact):
    def __init__(self):
        name = "Planar shadow"
        cost = {Resource.CALM: 2, Resource.DEATH: 2}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 1)
            player.resources.add(Resource.CALM, 3)
            self.tap()

        def effect2(state, player):
            player.resources.remove(Resource.CALM, 1)
            # piocher 2 cartes
            for _ in range(2):
                if player.deck:
                    card = player.deck.pop(0)
                    player.hand.append(card)
                    print(f"{player.name} pioche {card.name}")
                else:
                    print(f"{player.name} n'a plus de cartes dans sa pioche.")
            # défausser 1 carte de la main
            if player.hand:
                print("Choisissez une carte à défausser :")
                card = choose_card(player.hand)
                player.hand.remove(card)
                player.discard.append(card)
                print(f"{player.name} défausse {card.name}")
            self.tap()

        abilities = [
            Ability("1 LIFE pour 3 CALM", cost={Resource.LIFE: 1}, effect=effect1),
            Ability("1 CALM pour piocher 2 cartes puis défausser 1", cost={Resource.CALM: 1}, effect=effect2)
        ]
        return abilities 


class DwarvenDraw(Artifact):
    def __init__(self):
        name = "Dwarven draw"
        cost = {Resource.ELAN: 1}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.ELAN, 1)
            player.resources.add(Resource.GOLD, 1)
            self.tap()

        abilities = [Ability("1 ELAN pour 1 GOLD", cost={Resource.ELAN: 1}, effect=effect)]
        return abilities

class ElementaryShard(Artifact):
    def __init__(self):
        name = "Elementary shard"
        cost = {}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez une ressource à produire :")
            resource = choose_resource([r for r in Resource.real() if r != Resource.PEARL])
            player.resources.add(resource, 1)
            self.tap()

        abilities = [Ability("Produit 1 ressource au choix", cost={}, effect=effect)]
        return abilities

class CalciferWell(Artifact):
    def __init__(self):
        name = "Calcifer well"
        cost = {Resource.ELAN: 2}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.LIFE, 1)
            player.resources.add(Resource.ELAN, 1)
            player.resources.add(Resource.DEATH, 1)
            self.tap()

        abilities = [Ability("1 LIFE pour 1 ELAN + 1 DEATH", cost={Resource.LIFE: 1}, effect=effect)]
        return abilities


class BoneDragon(Artifact):
    def __init__(self):
        super().__init__("Bone Dragon",
                         cost={Resource.DEATH: 4, Resource.LIFE: 1},
                         card_type=CardType.DRAGON)
    
    def score(self, state, player):
        return 1
    
    def get_abilities(self):
        def effect(state, player):
            targets = [p for p in state.players if p != player]
            for target in targets:
                # proposer l'esquive avec 1 DEATH
                if target.resources.has(Resource.DEATH, 1):
                    print(f"\n{target.name}, voulez-vous esquiver en payant 1 DEATH ?")
                    print("1 - Oui")
                    print("2 - Non")
                    choice = 0
                    while choice not in [1, 2]:
                        try:
                            choice = int(input("Votre choix : "))
                        except ValueError:
                            pass
                    if choice == 1:
                        target.resources.remove(Resource.DEATH, 1)
                        print(f"{target.name} esquive l'attaque !")
                        continue
                
                # sinon résoudre l'attaque
                state.engine.resolve_attack(target, damage=2)
            
            self.tap()
        
        return [Ability("Attaquer tous les adversaires (2 dégâts)", cost={}, effect=effect)]

def make_artifacts():
    return [Phoenix(),
            Prism(),
            LightFlask(),
            PlanarShadow(),
            DwarvenDraw(),
            ElementaryShard(),
            CalciferWell(),
            BoneDragon()]

ALL_ARTIFACTS = make_artifacts() + make_artifacts() + make_artifacts()