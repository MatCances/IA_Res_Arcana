from cards.base_card import Card
from utils.constant import Resource
from game.action import Action
from game.ability import Ability
from cli.input_handler import choose_resource

class Mage(Card):
    def __init__(self, name):
        super().__init__(name, cost={})
    

class Alchemist(Mage):
    def __init__(self):
        super().__init__(name="Alchemist")

    def get_abilities(self):
        def effect1(state, player):
            print("Obtenez 1 ressource :")
            resource = choose_resource(list(Resource))
            player.resources.add(resource, 1)
            self.tap()

        def effect2(state, player):
            print("Choisissez 4 ressources à payer :")
            for _ in range(4):
                resource = choose_resource(list(Resource))
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
        def effect(state, player):
            player.resources.remove(Resource.CALM, 1)
            player.resources.add(Resource.GOLD, 1)
            self.tap()
        
        abilities = [Ability("1 CALM pour 1 GOLD", cost={Resource.CALM: 1}, effect=effect)]
        return abilities

class Illusionist(Mage):
    def __init__(self):
        super().__init__(name="Illusionist")

    def collect_base(self, state, player):
        excluded = {Resource.GOLD, Resource.PEARL}
        choices = [r for r in Resource.real() if r not in excluded]
        
        print("Illusionist : choisissez une ressource à collecter :")
        resource = choose_resource(choices)
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
            
            resource = choose_resource(player.resources.available())
            player.resources.remove(resource, 1)
            
            card = player.deck.pop(0)
            player.hand.append(card)
            print(f"{player.name} pioche {card.name}")
            self.tap()
        
        return [Ability("1 ressource au choix pour piocher une carte", cost={Resource.ANY: 1}, effect=effect)]

        


ALL_MAGES = [Alchemist(),
             Necromancer(),
             Nautilian(),
             Illusionist(),
             Erudite()]