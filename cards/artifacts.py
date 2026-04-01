from cards.base_card import Card
from utils.constant import Resource, CardType, GameEvent
from game.ability import Ability
from cli.input_handler import choose_resource, choose_card


class Artifact(Card):
    def __init__(self, name, cost, card_type=CardType.NONE):
        super().__init__(name, cost=cost, card_type=card_type)
    
    def play(self, state, player):
        """Vérifie le coût et pose la carte sur le plateau"""
        if not player.can_buy(self):
            print(f" ! Pas assez de ressources pour jouer {self.name} !")
            return False

        reductions = player.get_applicable_reductions(self)

        if not reductions:
            # Pas de réduction : paiement normal
            for r, amount in self.cost.items():
                player.resources.remove(r, amount)
        else:
            # Réduction active : le joueur choisit les ressources qu'il paye
            total_reduc = sum(r["value"] for r in reductions)
            total_cost = sum(self.cost.values())
            reduced_cost = max(0, total_cost - total_reduc)

            print(f"Choisissez {reduced_cost} ressource(s) à payer pour {self.name} (réduction de {total_reduc}) :")
            choices = [r for r, amount in self.cost.items() if player.resources.has(r, 1)]
            for _ in range(reduced_cost):
                resource = choose_resource(choices)
                player.resources.remove(resource, 1)
                choices = [r for r, amount in self.cost.items() if player.resources.has(r, 1)]

        # Ajoute la carte au plateau du joueur et la retire de sa main
        player.board.append(self)
        player.hand.remove(self)
        return True

    def destroy(self, state, player):
        state.engine.dispatch_event(GameEvent.DESTROY_ARTIFACT, None)
        player.board.remove(self)
        player.discard.append(self)
    
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
                resource = choose_resource([r for r in Resource.real() if r not in {Resource.PEARL, Resource.GOLD}])
                player.resources.add(resource, 1)
            print("Vous recevez 2 ressources")

class Phoenix(Artifact):
    def __init__(self):
        name = "Phénix"
        cost = {Resource.ELAN: 3, Resource.LIFE: 1}
        super().__init__(name, cost, card_type=CardType.CREATURE)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.add(Resource.GOLD, 1)
            self.tap()

        abilities = [Ability("Obtiens 1 GOLD", cost={}, effect=effect)]
        return abilities

class Prism(Artifact):
    def __init__(self):
        name = "Prisme"
        cost = {}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect1(state, player):
            print("Choisissez 1 ressource à payer :")
            resource = choose_resource(player.resources.available(excluded={Resource.PEARL}))
            player.resources.remove(resource, 1)
            print("Choisissez 2 ressources à recevoir :")
            for _ in range(2):
                r = choose_resource([r for r in Resource.real() if r not in [Resource.PEARL, Resource.GOLD]])
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
            cible = choose_resource([r for r in Resource.real() if r not in [Resource.PEARL, Resource.GOLD]])
            player.resources.remove(source, amount)
            player.resources.add(cible, amount)
            print(f"{player.name} convertit {amount} {source.value} en {cible.value}.")
            self.tap()
        
        abilities = [Ability("1 ressource contre 2 ressources", cost={Resource.ANY: 1}, effect=effect1),
                     Ability("Convertit toutes les ressources d'un type", cost={Resource.ANY: 1}, effect=effect2)]
        return abilities


class LightFlask(Artifact):
    def __init__(self):
        name = "Flasque de lumière"
        cost = {}
        super().__init__(name, cost)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.DESTROY_ARTIFACT:
            owner = next(p for p in state.players if self in p.board)
            print(f"\n[Réaction] {owner.name} : voulez-vous activer {self.name} ? (1 CALM)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                excluded = {Resource.DEATH, Resource.GOLD, Resource.PEARL}
                choices = [r for r in Resource.real() if r not in excluded]
                resource = choose_resource(choices)
                owner.resources.add(resource, 1)

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
        name = "Ombre planaire"
        cost = {Resource.CALM: 2, Resource.DEATH: 2}
        super().__init__(name, cost, card_type=CardType.DEMON)
    
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
        name = "Pioche des nains"
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
        name = "Eclat elementaire"
        cost = {}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez une ressource à produire :")
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]
            resource = choose_resource(choices)
            player.resources.add(resource, 1)
            self.tap()

        abilities = [Ability("Produit 1 ressource au choix", cost={}, effect=effect)]
        return abilities

class CalciferWell(Artifact):
    def __init__(self):
        name = "Puit Calcifère"
        cost = {Resource.ELAN: 2}
        super().__init__(name, cost)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.ELAN, 1)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.LIFE, 1)
            player.resources.add(Resource.ELAN, 1)
            player.resources.add(Resource.DEATH, 1)
            self.tap()

        abilities = [Ability("1 LIFE pour 1 ELAN + 1 DEATH", cost={Resource.LIFE: 1}, effect=effect)]
        return abilities


class Trident(Artifact):
    def __init__(self):
        super().__init__(
            name="Trident",
            cost={Resource.ELAN: 1, Resource.CALM: 1, Resource.DEATH: 1}
        )

    def collect_base(self, state, player):
        choices = [Resource.LIFE, Resource.CALM]  # CALM et LIFE
        print("Trident : choisissez une ressource à collecter (CALM ou LIFE) :")
        resource = choose_resource(choices)
        player.resources.add(resource, 1)

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 3)
            player.resources.add(Resource.PEARL, 1)
            self.tap()

        def effect2(state, player):
            player.resources.remove(Resource.PEARL, 1)
            excluded = {Resource.PEARL, Resource.GOLD}
            choices = [r for r in Resource.real() if r not in excluded]
            print("Choisissez 6 ressources à poser sur le Trident :")
            for _ in range(6):
                resource = choose_resource(choices)
                self.resources_on.add(resource, 1)
            # Ne s'engage pas

        return [
            Ability("3 LIFE pour 1 PEARL", cost={Resource.LIFE: 3}, effect=effect1),
            Ability("1 PEARL pour poser 6 ressources sur le Trident", cost={Resource.PEARL: 1}, effect=effect2)
        ]


class DragonEgg(Artifact):
    def __init__(self):
        super().__init__(
            name="Oeuf de dragon",
            cost={Resource.GOLD: 1}
        )

    def score(self, state, player):
        return 1

    def get_abilities(self):
        def effect(state, player):
            self.reduction_effect = {"value": 4,
                                     "excluded": [Resource.PEARL],
                                     "card_type": [CardType.DRAGON]}
            dragons = [c for c in player.hand
                       if (c.card_type == CardType.DRAGON and player.can_buy(c))]
            if not dragons:
                print("Vous n'avez aucun dragon en main que vous pouvez poser à -4.")
                return

            print("Choisissez un dragon à poser :")
            dragon = choose_card(dragons)
            dragon.play(state, player)

            # Se détruit : quitte le board et va en défausse
            self.reduction_effect = None
            self.destroy(state, player)

        return [Ability("Se détruire pour poser un dragon à -4", cost={}, effect=effect)]


class BoneDragon(Artifact):
    def __init__(self):
        super().__init__("Dragon d'os",
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


class ElementarySource(Artifact):
    def __init__(self):
        name = "Source Elementaire"
        cost = {Resource.ELAN: 2, Resource.LIFE: 1, Resource.CALM: 1}
        super().__init__(name, cost)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.LIFE, 1)
        player.resources.add(Resource.ELAN, 1)
        player.resources.add(Resource.CALM, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK:
            owner = next(p for p in state.players if self in p.board)
            if not owner.resources.has(Resource.CALM, 1):
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous activer {self.name} ? (1 CALM)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                owner.resources.remove(Resource.CALM, 1)
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")


class ElvishBow(Artifact):
    def __init__(self):
        super().__init__(
            name="Arc Elfique",
            cost={Resource.ELAN: 2, Resource.LIFE: 1},
            card_type=CardType.NONE
        )

    def get_abilities(self):
        def effect1(state, player):
            targets = [p for p in state.players if p != player]
            for target in targets:
                state.engine.resolve_attack(target, damage=1)
            self.tap()

        def effect2(state, player):
            if player.deck:
                card = player.deck.pop(0)
                player.hand.append(card)
                print(f"{player.name} pioche {card.name}")
            else:
                print(f"{player.name} n'a plus de cartes dans sa pioche.")
            self.tap()

        return [
            Ability("Attaquer tous les adversaires (1 dégât)", cost={}, effect=effect1),
            Ability("Piocher une carte", cost={}, effect=effect2)
        ]


class Automate(Artifact):
    def __init__(self):
        super().__init__(name="Automate",
                         cost={Resource.GOLD: 1,
                               Resource.ELAN: 1,
                               Resource.LIFE: 1,
                               Resource.CALM: 1})

    def collect_base(self, state, player):        
        for res in self.resources_on.available():
            self.resources_on.add(res, 2)

    def get_abilities(self):
        def effect(state, player):
            print("Choisissez une ressource à mettre sur l'automate: ")
            resource = choose_resource(player.resources.available())
            self.resources_on.add(resource, 1)
            player.resources.remove(resource, 1)
            self.tap()
            print(f"{player.name} pose {resource.value} sur l'Automate")

        abilities = [Ability("Poser une ressource sur l'Automate",
                             cost={Resource.ANY: 1},
                             effect=effect)]
        return abilities


class Siren(Artifact):
    def __init__(self):
        name = "Sirene"
        cost = {Resource.CALM: 2, Resource.LIFE: 2}
        card_type = CardType.CREATURE
        super().__init__(name, cost, card_type)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.CALM, 1)
    
    def get_abilities(self):
        def effect(state, player):
            if not player.resources.available():
                print("Vous n'avez aucune ressource à payer.")
                return
            
            excluded = {Resource.PEARL, Resource.DEATH, Resource.ELAN}
            print("Choisissez une ressource à payer :")
            resource = choose_resource(player.resources.available(excluded))
            player.resources.remove(resource, 1)

            if not player.board:
                print("Vous n'avez aucune carte sur le plateau.")
                return
            
            print("Choisissez une carte sur laquelle poser la ressource :")
            card = choose_card(player.board)
            card.resources_on.add(resource, 1)
            print(f"{resource.value} posé sur {card.name}")
            self.tap()
        return [Ability("Placer une ressource sur une carte", {Resource.ANY: 1}, effect=effect)]


class Homonculus(Artifact):
    def __init__(self):
        super().__init__(name="Homonculus",
                         cost={Resource.LIFE: 1},
                         card_type=CardType.DEMON)
        self.reduction_effect = {"value": 2,
                                 "excluded": [Resource.PEARL],
                                 "card_type": [CardType.DEMON]}

    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 2 ressources à mettre sur la carte:")
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]
            for _ in range(2):
                resource = choose_resource(choices)
                self.resources_on.add(resource, 1)
            self.tap()

        abilities = [Ability("2 ressource sur la carte",
                             cost={},
                             effect=effect)]
        return abilities


class PrismaticDragon(Artifact):
    def __init__(self):
        super().__init__(name="Dragon Prismatique",
                         cost={Resource.ELAN: 2, Resource.LIFE: 2, Resource.CALM: 2},
                         card_type=CardType.DRAGON)
    
    def score(self, state, player):
        return 1
    
    def collect_base(self, state, player):
        excluded = {Resource.PEARL, Resource.GOLD, Resource.DEATH}
        choices = [r for r in Resource.real() if r not in excluded]
        resource = choose_resource(choices)
        player.resources.add(resource, 1)
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 4 ressources à mettre sur la carte:")
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]
            for _ in range(4):
                resource = choose_resource(choices)
                self.resources_on.add(resource, 1)
            self.tap()

        abilities = [Ability("1 GOLD pour 4 ressources sur la carte",
                             cost={Resource.GOLD: 1},
                             effect=effect)]
        return abilities


class DurtDragon(Artifact):
    def __init__(self):
        super().__init__(name="Dragon de Terre",
                         cost={Resource.ELAN: 4, Resource.LIFE: 3},
                         card_type=CardType.DRAGON)
    
    def score(self, state, player):
        return 1
    
    def get_abilities(self):
        def effect(state, player):
            targets = [p for p in state.players if p != player]
            for target in targets:
                # proposer l'esquive avec 1 GOLD
                if target.resources.has(Resource.GOLD, 1):
                    print(f"\n{target.name}, voulez-vous esquiver en payant 1 GOLD ?")
                    print("1 - Oui")
                    print("2 - Non")
                    choice = 0
                    while choice not in [1, 2]:
                        try:
                            choice = int(input("Votre choix : "))
                        except ValueError:
                            pass
                    if choice == 1:
                        target.resources.remove(Resource.GOLD, 1)
                        print(f"{target.name} esquive l'attaque !")
                        continue
                
                # sinon résoudre l'attaque
                state.engine.resolve_attack(target, damage=2)
            
            self.tap()
        
        return [Ability("Attaquer tous les adversaires (2 dégâts)", cost={}, effect=effect)]


class Dolfin(Artifact):
    def __init__(self):
        super().__init__(name="Dauphin",
                         cost={Resource.GOLD: 2, Resource.LIFE: 2, Resource.CALM: 2},
                         card_type=CardType.CREATURE)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.PEARL, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK:
            owner = next(p for p in state.players if self in p.board)
            if not owner.resources.has(Resource.CALM, 1):
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous activer {self.name} ? (1 CALM)")
            print("1 - Oui")
            print("2 - Non")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                owner.resources.remove(Resource.CALM, 1)
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")

    def get_abilities(self):
        def effect(state, player):
            player.resources.add(Resource.CALM, 3)

            targets = [p for p in state.players if p != player]
            for target in targets:
                target.resources.add(Resource.CALM, 1)
            
            self.tap()
        
        abilities = [Ability("+3 CALM, tous les adversaires: +1 CALM",
                             cost={},
                             effect=effect)]
        return abilities


class OrnateStatuette(Artifact):
    def __init__(self):
        super().__init__(name="Statuette Ornée",
                         cost={Resource.DEATH: 2, Resource.GOLD: 1})
    
    def score(self, state, player):
        return 1
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.add(Resource.DEATH, 3)

            targets = [p for p in state.players if p != player]
            for target in targets:
                target.resources.add(Resource.DEATH, 1)
            
            self.tap()
        
        def effect2(state, player):
            player.resources.add(Resource.GOLD, 2)
            player.resources.add(Resource.ELAN, 1)
            self.destroy(state, player)
        
        abilities = [Ability("+3 DEATH, tous les adversaires: +1 DEATH",
                             cost={},
                             effect=effect1),
                    Ability("Détruire la carte: +2 GOLD, +1 ELAN",
                            cost={},
                            effect=effect2)]
        return abilities


class Shrivatsa(Artifact):
    def __init__(self):
        super().__init__(name="Shrivatsa", cost={})
    
    def collect_base(self, state, player):
        if Resource.PEARL in self.resources_on.available():
            print(f"{self.name}: Collecter 1 GOLD ou 2 ressources au choix ?")
            print("1 - +1 GOLD")
            print("2 - +2 Ressources au choix")
            choice = 0
            while choice not in [1, 2]:
                try:
                    choice = int(input("Votre choix : "))
                except ValueError:
                    pass
            if choice == 1:
                player.resources.add(Resource.GOLD, 1)
            elif choice == 2:
                print("Choisissez 2 ressources")
                excluded = [Resource.PEARL, Resource.GOLD]
                choices = [r for r in Resource.real() if r not in excluded]
                for _ in range(2):
                    res = choose_resource(choices)
                    player.resources.add(res, 1)
    
    def get_abilities(self):
        def effect(state, player):
            self.resources_on.add(Resource.PEARL, 1)
            self.tap()

        abilities = [Ability(f"Mettre une PEARL sur {self.name}",
                             cost={Resource.PEARL: 1},
                             effect=effect)]
        return abilities


class FireChalice(Artifact):
    def __init__(self):
        super().__init__(name="Coupe de Feu",
                         cost={Resource.GOLD: 1, Resource.ELAN: 1})
    
    def collect_base(self, state, player):
        player.resources.add(Resource.ELAN, 2)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.ELAN, 1)
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée.")
                self.tap()
                return
            
            print("Choisissez une carte à désengager: ")
            card = choose_card(tapped)
            card.untap()
            self.tap()

        abilities = [Ability("1 ELAN pour désengager une carte",
                             cost={Resource.ELAN: 1},
                             effect=effect)]
        return abilities


class Moloss(Artifact):
    def __init__(self):
        super().__init__(name="Molosse",
                         cost={Resource.ELAN: 1},
                         card_type=CardType.CREATURE)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK:
            owner = next(p for p in state.players if self in p.board)
            print(f"\n[Réaction] {owner.name} : voulez-vous engager {self.name} ?")
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

    def get_abilities(self):
        # Cet effet doit se faire justement si la carte est engagé.
        # Le problème c'est que get_abilities n'est appelé que si la carte n'est pas engagé
        # j'ai géré ca dans le input handler, exception pour le Molosse
        def effect(state, player):
            player.resources.remove(Resource.ELAN, 1)
            self.untap()

        abilities = [Ability("1 ELAN pour désengager le Molosse",
                             cost={Resource.ELAN: 1},
                             effect=effect)]
        return abilities


class FireDragon(Artifact):
    def __init__(self):
        super().__init__(name="Dragon de Feu",
                         cost={Resource.ELAN: 6},
                         card_type=CardType.DRAGON)
    
    def score(self, state, player):
        return 1
    
    def get_abilities(self):
        def effect(state, player):
            targets = [p for p in state.players if p != player]
            for target in targets:
                # proposer l'esquive avec 1 CALM
                if target.resources.has(Resource.CALM, 1):
                    print(f"\n{target.name}, voulez-vous esquiver en payant 1 CALM ?")
                    print("1 - Oui")
                    print("2 - Non")
                    choice = 0
                    while choice not in [1, 2]:
                        try:
                            choice = int(input("Votre choix : "))
                        except ValueError:
                            pass
                    if choice == 1:
                        target.resources.remove(Resource.CALM, 1)
                        print(f"{target.name} esquive l'attaque !")
                        continue
                
                # sinon résoudre l'attaque
                state.engine.resolve_attack(target, damage=2)
            
            self.tap()
        
        return [Ability("Attaquer tous les adversaires (2 dégâts)", cost={}, effect=effect)]


class KeenSword(Artifact):
    def __init__(self):
        super().__init__(name="Epée Vive",
                         cost={Resource.GOLD: 1, Resource.ELAN: 1})
    
    def collect_base(self, state, player):
        player.resources.add(Resource.DEATH, 1)
        player.resources.add(Resource.ELAN, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK:
            owner = next(p for p in state.players if self in p.board)
            if not owner.resources.has(Resource.ELAN, 1):
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous activer {self.name} ? (1 ELAN, pose 1 DEATH sur la carte)")
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
                self.resources_on.add(Resource.DEATH, 1)
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")


class GoldLion(Artifact):
    def __init__(self):
        super().__init__(name="Lion d'Or",
                         cost={Resource.ELAN: 2, Resource.LIFE: 1, Resource.CALM: 1, Resource.GOLD: 1},
                         card_type=CardType.CREATURE)
    
    def score(self, state, player):
        return 1
    
    def collect_base(self, state, player):
        player.resources.add(Resource.CALM, 1)
        player.resources.add(Resource.LIFE, 1)
        player.resources.add(Resource.ELAN, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            if not owner.resources.has(Resource.ELAN, 1):
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous engager {self.name} ?")
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


class LifeChalice(Artifact):
    def __init__(self):
        super().__init__(name="Calice de Vie",
                         cost={Resource.GOLD: 1, Resource.LIFE: 1, Resource.CALM: 1})
    
    def collect_base(self, state, player):
        player.resources.add(Resource.CALM, 1)
        player.resources.add(Resource.LIFE, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            if not owner.resources.has(Resource.ELAN, 1):
                return
            print(f"\n[Réaction] {owner.name} : voulez-vous engager {self.name} ?")
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
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.CALM, 2)
            self.resources_on.add(Resource.CALM, 2)
            self.resources_on.add(Resource.LIFE, 1)
        
        abilities = [Ability(f"2 CALM pour mettre 2 CALM et 1 LIFE sur {self.name}",
                             cost={Resource.CALM: 2},
                             effect=effect)]
        return abilities


class MidasRing(Artifact):
    def __init__(self):
        super().__init__(name="Anneau de Midas",
                         cost={Resource.GOLD: 1, Resource.LIFE: 1})
    
    def score(self, state, player):
        return 1
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 2)
            self.resources_on.add(Resource.GOLD, 1)
        
        def effect2(state, player):
            self.resources_on.add(Resource.GOLD, 1)
            self.tap()
        
        abilities = [Ability(f"2 LIFE pour mettre 1 GOLD sur {self.name}",
                             cost={Resource.LIFE: 2},
                             effect=effect1),
                    Ability(f"Engager {self.name} pour mettre 1 GOLD dessus",
                            cost={},
                            effect=effect2)]
        return abilities


class CursedSkull(Artifact):
    def __init__(self):
        super().__init__(name="Crane Maudit",
                         cost={Resource.DEATH: 2})
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.LIFE, 1)
            excluded = [Resource.PEARL, Resource.GOLD, Resource.LIFE]
            choices = [r for r in Resource.real() if r not in excluded]
            for _ in range(3):
                resource = choose_resource(choices)
                self.resources_on.add(resource, 1)
        
        abilities = [Ability(f"1 LIFE pour mettre 3 ressources sur {self.name} (sauf LIFE, GOLD)",
                             cost={Resource.LIFE: 1},
                             effect=effect)]
        return abilities


class OldDragon(Artifact):
    def __init__(self):
        super().__init__(name="Dragon Ancien",
                         cost={Resource.DEATH: 6, Resource.LIFE: 6},
                         card_type=CardType.DRAGON)
    
    def score(self, state, player):
        return 2
    
    def get_abilities(self):
        def effect(state, player):
            targets = [p for p in state.players if p != player]
            for target in targets:
                # proposer l'esquive avec 2 GOLD ou 1 PEARL
                if target.resources.has(Resource.GOLD, 2) or target.resources.has(Resource.PEARL, 1):
                    print(f"\n{target.name}, voulez-vous esquiver en payant 2 GOLD ou 1 PEARL ?")
                    print("1 - Oui 2 GOLD")
                    print("2 - Oui 1 PEARL")
                    print("3 - Non")
                    choice = 0
                    while choice not in [1, 2, 3]:
                        try:
                            choice = int(input("Votre choix : "))
                        except ValueError:
                            pass
                    if choice == 1:
                        target.resources.remove(Resource.GOLD, 2)
                        print(f"{target.name} esquive l'attaque !")
                        continue
                    elif choice == 2:
                        target.resources.remove(Resource.PEARL, 1)
                        print(f"{target.name} esquive l'attaque !")
                        continue
                
                # sinon résoudre l'attaque
                state.engine.resolve_attack(target, damage=3)
            
            self.tap()
        
        return [Ability("Attaquer tous les adversaires (3 dégâts)", cost={}, effect=effect)]


class DragonTeeth(Artifact):
    def __init__(self):
        super().__init__(name="Dent de Dragon",
                         cost={Resource.ELAN: 1, Resource.DEATH: 1})
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.ELAN, 2)
            self.resources_on.add(Resource.ELAN, 3)
        
        def effect2(state, player):
            # Le dragon ancien ne peut pas etre mis avec la dent du dragon
            dragons = [c for c in player.hand
                       if c.card_type == CardType.DRAGON and not isinstance(c, OldDragon)]
            if not dragons:
                print("Vous n'avez aucun dragon en main que vous pouvez poser.")
                return

            print("Choisissez un dragon à poser à 0 :")
            dragon = choose_card(dragons)
            player.board.append(dragon)
            player.hand.remove(dragon)
            print(f"{player.name} joue {dragon.name} à 0.")
        
        abilities = [Ability(f"2 ELAN pour mettre 3 ELAN sur {self.name}",
                             cost={Resource.ELAN: 2},
                             effect=effect1),
                    Ability(f"Engager {self.name} pour mettre un dragon à 0",
                             cost={Resource.ELAN: 3},
                             effect=effect2)]
        return abilities

def make_artifacts():
    return [Phoenix(),
            Prism(),
            LightFlask(),
            PlanarShadow(),
            DwarvenDraw(),
            ElementaryShard(),
            CalciferWell(),
            BoneDragon(),
            ElementarySource(),
            Siren(),
            ElvishBow(),
            Automate(),
            DragonEgg(),
            Trident(),
            DurtDragon(),
            Shrivatsa(),
            OrnateStatuette(),
            Dolfin(),
            FireChalice(),
            Moloss(),
            FireDragon(),
            PrismaticDragon(),
            KeenSword(),
            LifeChalice(),
            Homonculus(),
            MidasRing(),
            CursedSkull(),
            OldDragon(),
            DragonTeeth(),
            GoldLion()]

ALL_ARTIFACTS = make_artifacts()