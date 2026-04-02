from cards.base_card import Card
from utils.constant import Resource, CardType, GameEvent
from game.action import Action
from game.ability import Ability
# from cli.input_handler import choose_resource, choose_card

class Mage(Card):
    def __init__(self, name):
        super().__init__(name, cost={})
    

class Alchemist(Mage):
    def __init__(self):
        super().__init__(name="Alchemist")

    def get_abilities(self):
        def effect1(state, player):
            print("Obtenez 1 ressource :")
            resource = player.choose_resource([r for r in Resource.real() if r != Resource.PEARL])
            player.resources.add(resource, 1)
            self.tap()

        def effect2(state, player):
            print("Choisissez 4 ressources à payer :")
            for _ in range(4):
                
                resource = player.choose_resource(list(Resource.real()))
                player.resources.remove(resource, 1)
            player.resources.add(Resource.GOLD, 2)
            self.tap()
        
        abilities = [
            Ability("Obtiens 1 Ressource", cost={}, effect=effect1),
            Ability("4 Ressources pour 2 GOLD", cost={Resource.ANY: 4}, effect=effect2)
        ]
        return abilities


class Necromancer(Mage):
    def __init__(self):
        super().__init__(name="Necromancer")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.DEATH, 1)
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.LIFE, 2)
            self.resources_on.add(Resource.DEATH, 3)
            self.tap()
        
        abilities = [Ability("2 LIFE pour 3 DEATH", cost={Resource.LIFE: 2}, effect=effect)]
        return abilities

class Nautilian(Mage):
    def __init__(self):
        super().__init__(name="Nautilian")
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.CALM, 1)
            player.resources.add(Resource.GOLD, 1)
            self.tap()
        
        def effect2(state, player):
            player.resources.remove(Resource.CALM, 2)
            self.resources_on.add(Resource.PEARL, 1)
            self.tap()
        
        abilities = [Ability("1 CALM pour 1 GOLD", cost={Resource.CALM: 1}, effect=effect1),
                     Ability("2 CALM pour 1 PEARL sur la carte", cost={Resource.CALM: 2}, effect=effect2)
                     ]
        return abilities

class Illusionist(Mage):
    def __init__(self):
        super().__init__(name="Illusionist")
        self.card_type = CardType.ILLUSIONIST

    def collect_base(self, state, player):
        excluded = {Resource.GOLD, Resource.PEARL}
        choices = [r for r in Resource.real() if r not in excluded]
        
        print("Illusionist : choisissez une ressource à collecter :")
        resource = player.choose_resource(choices)
        player.resources.add(resource, 1)
    
    def get_abilities(self):
        return super().get_abilities()


class Erudite(Mage):
    def __init__(self):
        super().__init__(name="Erudite")
    
    def get_abilities(self):
        def effect(state, player):
            if not player.deck:
                print(f"{player.name} n'a plus de cartes dans sa pioche.")
                return
            
            resource = player.choose_resource(player.resources.available())
            player.resources.remove(resource, 1)
            
            card = player.deck.pop(0)
            player.hand.append(card)
            print(f"{player.name} pioche {card.name}")
            self.tap()
        
        return [Ability("1 ressource au choix pour piocher une carte", cost={Resource.ANY: 1}, effect=effect)]


class Distiller(Mage):
    def __init__(self):
        super().__init__(name=("Distiller"))

    def get_abilities(self):
        def effect1(state, player):
            print("Obtenez 1 CALM :")
            player.resources.add(Resource.CALM, 1)
            self.tap()

        def effect2(state, player):
            print("Payer une ressource pour la placer sur une carte")
            if not player.resources.available():
                print("Vous n'avez aucune ressource à payer.")
                return
            
            print("Choisissez une ressource à payer :")
            excluded = {Resource.PEARL}
            resource = player.choose_resource(player.resources.available(excluded=excluded))
            player.resources.remove(resource, 1)

            if not player.board:
                print("Vous n'avez aucune carte sur le plateau.")
                return
            
            print("Choisissez une carte sur laquelle poser la ressource :")
            card = player.choose_card(player.board)
            card.resources_on.add(resource, 1)
            print(f"{resource.value} posé sur {card.name}")
            self.tap()
        
        def effect3(state, player):
            print("Payer un GOLD et une PEARL pour la placer sur une carte")
            
            player.resources.remove(Resource.GOLD, 1)
            player.resources.remove(Resource.PEARL, 1)

            if not player.board:
                print("Vous n'avez aucune carte sur le plateau.")
                return
            
            print("Choisissez une carte sur laquelle poser la perle :")
            card = player.choose_card(player.board)
            card.resources_on.add(Resource.PEARL, 1)
            print(f"pearl posé sur {card.name}")
            self.tap()
        
        abilities = [
            Ability("Obtiens 1 CALM", cost={}, effect=effect1),
            Ability("Payer une ressource pour la placer sur une carte", cost={Resource.ANY: 1}, effect=effect2),
            Ability("Payer un GOLD et une PEARL pour la placer sur une carte", cost={Resource.GOLD: 1, Resource.PEARL: 1}, effect=effect3)
        ]
        return abilities


class Demonist(Mage):
    def __init__(self):
        super().__init__(name="Demonist")
    
    def get_abilities(self):
        def effect1(state, player):
            print("Payez un LIFE pour récupérer une carte")
            if not player.discard:
                print(f"{player.name} n'a aucune carte dans sa défausse.")
                return
            
            player.resources.remove(Resource.LIFE, 1)
            print("Choisissez une carte à récupérer :")
            card = player.choose_card(player.discard)
            player.discard.remove(card)
            player.hand.append(card)
            print(f"{player.name} récupère {card.name}")
        
        def effect2(state, player):
            print("Réanimez un démon ")
            tapped = [card for card in player.board if card.is_tapped and card.card_type is CardType.DEMON]
            if not tapped:
                print("Aucun démon engagée.")
                self.tap()
                return
            
            print("Choisissez un démon à désengager: ")
            card = player.choose_card(tapped)
            card.untap()
            self.tap()
        
        return [Ability("1 LIFE pour récupérer une carte de la défausse", cost={Resource.LIFE: 1}, effect=effect1),
                Ability("Désengager un démon", cost={}, effect=effect2)
                ]


class Tamer(Mage):
    def __init__(self):
        super().__init__(name="Dresseuse")
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 1)
            self.resources_on.add(Resource.LIFE, 3)
            self.tap()
        
        def effect2(state, player):
            untapped = [card for card in player.board if not card.is_tapped and card.card_type is CardType.CREATURE]
            if not untapped:
                print("Aucune créature à engager")
                self.tap()
                return

            print("Choisissez une créature à engager: ")
            card = player.choose_card(untapped)
            card.tap()
            self.tap()

        abilities = [Ability("1 LIFE pour mettre 3 LIFE sur Dresseuse", cost={Resource.LIFE: 1}, effect=effect1),
                     Ability("Engage Dresseuse et une créature pour obtenir 2 ressource", cost={}, effect=effect2)]
        return abilities


class Bard(Mage):
    def __init__(self):
        super().__init__(name="Barde")
    
    def get_abilities(self):
        def effect1(state, player):
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]

            print("Choisissez une ressource: ")
            resource = player.choose_resource(choices)
            player.resources.add(resource, 1)
            self.tap()

        def effect2(state, player):
            ok_types = {CardType.DEMON, CardType.DRAGON, CardType.CREATURE}
            hand_with_type = [card for card in player.hand if card.card_type in ok_types]
            if not hand_with_type:
                print("Aucune créature/démon/dragon à défausser")
                self.tap()
                return
            
            print("Choisissez un démon/dragon/créature à défausser")
            card = player.choose_card(hand_with_type)
            player.hand.remove(card)
            player.discard.append(card)
            player.resources.add(Resource.GOLD, 2)
            self.tap()

        abilities = [Ability("Obtiens une ressource au choix", cost={}, effect=effect1),
                     Ability("Défausse créature, dragon ou demon: +2 GOLD", cost={}, effect=effect2)]
        return abilities


class Seer(Mage):
    def __init__(self):
        super().__init__(name="Voyante")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.CALM, 1)

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
                deck = state.monuments_deck
            
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


class Duelist(Mage):
    def __init__(self):
        super().__init__(name="Duelliste")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.ELAN, 1)

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.DEATH, 1)
            self.resources_on.add(Resource.GOLD, 1)
            self.tap()
        return [Ability("1 DEATH pour 1 GOLD sur la carte", cost={Resource.DEATH: 1}, effect=effect1)]


class Druidess(Mage):
    def __init__(self):
        super().__init__(name="Druidesse")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.LIFE, 1)

    def get_abilities(self):
        def effect(state, player):
            tapped_creature = [card for card in player.board if card.is_tapped and card.card_type is CardType.CREATURE]
            if not tapped_creature:
                print("Aucune créature à désengager")
                self.tap()
                return
            
            card = player.choose_card(tapped_creature)
            card.untap()
            self.tap()

        return [Ability("Désengager une créature", cost={}, effect=effect)]


class Witch(Mage):
    def __init__(self):
        super().__init__(name="Sorcière")
    
    def collect_base(self, state, player):
        choices = {Resource.LIFE, Resource.DEATH}
        print("Sorcière : choisissez une ressource à collecter :")
        resource = player.choose_resource(choices)
        player.resources.add(resource, 1)

    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 2 ressources à payer :")
            for _ in range(2):
                resource = player.choose_resource(player.resources.available(excluded={Resource.ANY, Resource.PEARL}))
                player.resources.remove(resource, 1)
            
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée.")
                self.tap()
                return
            
            print("Choisissez une carte à désengager: ")
            card = player.choose_card(tapped)
            card.untap()
            self.tap()

        abilities = [Ability("2 ressource au choix pour désengager une carte", cost={Resource.ANY: 2}, effect=effect)]
        return abilities


class SoothSayer(Mage):
    def __init__(self):
        super().__init__(name="Devin")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.ELAN, 1)
    
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
                card = player.choose_card(player.hand)
                player.hand.remove(card)
                player.discard.append(card)
                print(f"{player.name} défausse {card.name}")
            
            self.tap()
        
        return [Ability("Piocher 3 cartes puis défausser 3 cartes", cost={}, effect=effect)]


class Transmuter(Mage):
    def __init__(self):
        super().__init__(name="Transmutatrice")
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez 2 ressources à payer :")
            for _ in range(2):
                resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}))
                player.resources.remove(resource, 1)
            
            excluded = {Resource.GOLD, Resource.PEARL}
            choices = [r for r in Resource.real() if r not in excluded]
            print("Choisissez 3 ressources à recevoir :")
            for _ in range(3):
                resource = player.choose_resource(choices)
                player.resources.add(resource, 1)
            
            self.tap()
        
        return [Ability("2 ressources pour 3 ressources (sauf gold et pearl)", cost={Resource.ANY: 2}, effect=effect)]


class Healer(Mage):
    def __init__(self):
        super().__init__(name="Guérisseur")
    
    def collect_base(self, state, player):
        choices = (Resource.CALM, Resource.LIFE)
        print("Guérisseur : choisissez une ressource à collecter :")
        resource = player.choose_resource(choices)
        player.resources.add(resource, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            
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


class Artificer(Mage):
    def __init__(self):
        super().__init__(name="Artificier")
        self.reduction_effect = {"value": 1,
                                 "excluded": [Resource.GOLD, Resource.PEARL],
                                 "card_type": [None, CardType.CREATURE, CardType.DEMON, CardType.DRAGON]}



class Draconist(Mage):
    def __init__(self):
        super().__init__("Draconiste")
    
    def collect_base(self, state, player):
        player.resources.add(Resource.ELAN, 1)
    
    def get_abilities(self):
        def effect1(state, player):
            choices = [c for c in player.hand if c.card_type == CardType.DRAGON]

            if not choices:
                print("Vous n'avez pas de dragon en main")
                return

            print("Choisissez un dragon de votre main:")
            dragon = player.choose_card(choices)
            self.reduction_effect = {"value": 2,
                                     "excluded": [Resource.PEARL],
                                     "card_type": [CardType.DRAGON]}

            if not player.can_buy(dragon):
                print(f"Pas assez de ressource pour jouer {dragon.name}")
                return
            
            # Récup la valeur totale de reduction (draconniste + autres cartes s'il y a)
            reductions = player.get_applicable_reductions(dragon)
            total_reduc = sum([reduc["value"] for reduc in reductions])
            total_cost = sum(val for _, val in dragon.cost.items())
            reduced_cost = total_cost - total_reduc

            print(f"Choisissez {reduced_cost} ressources à payer: ")
            choices = [r for r, _ in dragon.cost.items()]
            for _ in range(reduced_cost):
                resource = player.choose_resource(choices)
                player.resources.remove(resource, 1)
                # Update le choix des ressources si elles tombent à 0 lorsque le joueur choisit
                choices = [r for r, _ in dragon.cost.items() if player.resources.has(r, 1)]

            player.hand.remove(dragon)
            player.board.append(dragon)
            self.tap()
            self.reduction_effect = None
            print(f"{player.name} pose {dragon.name} à -{total_reduc}")

        def effect2(state, player):
            choices = [c for c in player.board if c.card_type == CardType.DRAGON and c.is_tapped]
            if not choices:
                print("Aucun dragon engagé en jeu")
                return

            print("Choisissez un dragon à revive:")
            dragon = player.choose_card(choices)
            dragon.untap()
            self.tap()
            print(f"{player.name} réanime {dragon.name} avec {self.name}")
        
        abilities = [
            Ability("Poser un dragon à -2", cost={}, effect=effect1),
            Ability("Revive un dragon", cost={}, effect=effect2)
        ]
        return abilities

ALL_MAGES = [Alchemist(),
             Necromancer(),
             Nautilian(),
             Illusionist(),
             Erudite(),
             Distiller(),
             Demonist(),
             Tamer(),
             Bard(),
             Seer(),
             Duelist(),
             Druidess(),
             Witch(),
             SoothSayer(),
             Transmuter(),
             Healer(),
             Artificer()]