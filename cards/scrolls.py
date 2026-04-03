from cards.base_card import Card
from utils.constant import Resource, GameEvent
from game.ability import Ability

class Scroll(Card):
    def __init__(self, name, cost):
        super().__init__(name, cost=cost)


class Vitality(Scroll):
    def __init__(self):
        super().__init__("Vitalité", cost={})
    
    def get_abilities(self):
        def effect(state, player):
            tapped = [card for card in player.board if card.is_tapped]
            if not tapped:
                print("Aucune carte engagée sur votre plateau.")
                return
            
            print("Choisissez une carte à désengager :")
            card = player.choose_card(tapped)
            card.untap()
            print(f"{card.name} est désengagée.")
            player.resources.remove(Resource.ELAN, 2)
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("Désengager une carte du plateau", cost={Resource.ELAN: 2}, effect=effect)]
    

class Shield(Scroll):
    def __init__(self):
        super().__init__("Bouclier", cost={})
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)
            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : utiliser Parchemin {self.name} ?"):
                kwargs.get('context')['cancelled'] = True
                owner.board.remove(self)
                state.scrolls.append(self)
                print(f"[Réaction] Bouclier : attaque annulée !")


class Disjunction(Scroll):
    def __init__(self):
        super().__init__("Disjonction", cost={Resource.GOLD: 1})
    
    def get_abilities(self):
        def effect(state, player):
            player.resources.remove(Resource.GOLD, 1)
            player.resources.add(Resource.ELAN, 1)
            player.resources.add(Resource.DEATH, 1)
            player.resources.add(Resource.LIFE, 1)
            player.resources.add(Resource.CALM, 1)
            print(f"{player.name} obtient 1 ELAN, 1 DEATH, 1 LIFE, 1 CALM")
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("1 GOLD pour 1 ELAN + 1 DEATH + 1 LIFE + 1 CALM", cost={Resource.GOLD: 1}, effect=effect)]


class Projection(Scroll):
    def __init__(self):
        super().__init__("Projection", cost={})
    
    def get_abilities(self):
        def effect(state, player):
            print("Choisissez une ressource: ")
            resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL, Resource.GOLD}))
            
            max_x = player.resources.get_amount(resource) // 3
            if max_x == 0:
                print(f"Vous n'avez pas assez de {resource.value} (minimum 3).")
                return
            
            print("Choisissez le nombre de GOLD à obtenir: ")
            x = player.choose_number(1, max_x)
            
            player.resources.remove(resource, 3 * x)
            player.resources.add(Resource.GOLD, x)
            print(f"{player.name} paie {3*x} {resource.value} et reçoit {x} GOLD")
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("3X ressources d'un même type pour X GOLD", cost={}, effect=effect)]


class Augur(Scroll):
    def __init__(self):
        super().__init__("Augure", cost={Resource.CALM: 1})
    
    def get_abilities(self):
        def effect(state, player):
            if not player.deck:
                print(f"{player.name} n'a plus de cartes dans sa pioche.")
                return
            
            player.resources.remove(Resource.CALM, 1)
            card = player.deck.pop(0)
            player.hand.append(card)
            print(f"{player.name} pioche {card.name}")
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("1 CALM pour piocher une carte", cost={Resource.CALM: 1}, effect=effect)]


class Destruction(Scroll):
    def __init__(self):
        super().__init__("Destruction", cost={})
    
    def get_abilities(self):
        def effect(state, player):
            from cards.artifacts import Artifact
            artifacts = [card for card in player.board if isinstance(card, Artifact)]
            if not artifacts:
                print("Aucun artefact sur votre plateau.")
                return
            
            print("Choisissez un artefact à détruire :")
            card = player.choose_card(artifacts)
            
            # calculer le total du coût
            total = sum(card.cost.values())
            
            # retirer l'artefact du board et le défausser
            player.board.remove(card)
            player.discard.append(card)
            print(f"{card.name} est détruit.")
            
            # recevoir autant de ressources que le coût total
            excluded = {Resource.PEARL, Resource.GOLD}
            choices = [r for r in Resource.real() if r not in excluded]
            print(f"Choisissez {total} ressource(s) à recevoir :")
            for _ in range(total):
                resource = player.choose_resource(choices)
                player.resources.add(resource, 1)
            
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("Détruire un artefact pour gagner son coût en ressources", cost={}, effect=effect)]


class Recovery(Scroll):
    def __init__(self):
        super().__init__("Récupération", cost={Resource.DEATH: 1})
    
    def get_abilities(self):
        def effect(state, player):
            if not player.discard:
                print(f"{player.name} n'a aucune carte dans sa défausse.")
                return
            
            player.resources.remove(Resource.DEATH, 1)
            print("Choisissez une carte à récupérer :")
            card = player.choose_card(player.discard)
            player.discard.remove(card)
            player.hand.append(card)
            print(f"{player.name} récupère {card.name}")
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("1 DEATH pour récupérer une carte de la défausse", cost={Resource.DEATH: 1}, effect=effect)]


class Transformation(Scroll):
    def __init__(self):
        super().__init__("Transformation", cost={})
    
    def get_abilities(self):
        def effect(state, player):

            print("Choisissez une ressource: ")
            resource_out = player.choose_resource(player.resources.available(excluded={Resource.PEARL}))
            
            print("Choisissez le nombre à échanger: ")
            max_x = player.resources.get_amount(resource_out)
            x = player.choose_number(1, max_x)
            
            excluded = {Resource.PEARL, Resource.GOLD}
            choices = [r for r in Resource.real() if r not in excluded]
            resource_in = player.choose_resource(choices)
            
            player.resources.remove(resource_out, x)
            player.resources.add(resource_in, x)
            print(f"{player.name} échange {x} {resource_out.value} contre {x} {resource_in.value}")
            player.board.remove(self)
            state.scrolls.append(self)
        
        return [Ability("X ressources d'un type contre X ressources d'un autre type",
                        cost={Resource.ANY: 1},
                        effect=effect)]

ALL_SCROLLS = [Vitality(),
               Shield(),
               Disjunction(),
               Projection(),
               Augur(),
               Destruction(),
               Recovery(),
               Transformation()]