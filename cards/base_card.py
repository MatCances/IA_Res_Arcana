from utils.resource_pool import ResourcePool
from utils.constant import CardType



class Card:
    def __init__(self, name, cost, card_type=CardType.NONE):
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.is_tapped = False
        self.reduction_effect = None

        # Les ressources presentes sur la carte
        self.resources_on = ResourcePool()
    
    def collect_base(self, state, player):
        """À surcharger dans chaque carte. Applique la collecte de base."""
        pass  # par défaut : rien

    def collect_stored(self, state, player):
        for resource, amount in self.resources_on.resources.items():
            if amount > 0:
                player.resources.add(resource, amount)
                self.resources_on.remove(resource, amount)

    def get_abilities(self):
        return []

    def tap(self):
        self.is_tapped = True
    
    def untap(self):
        self.is_tapped = False
    
    def score(self, state, player):
        """Point de la carte en fonction de l'état du jeu"""
        return 0
    
    def get_discount(self, card):
        return {}
    
    def on_event(self, event, state, source_player, **kwargs):
        """Réaction à un événement du jeu.
        
        Args:
            event (GameEvent): l'événement qui vient de se produire
            state (GameState): l'état du jeu
            source_player (Player): le joueur qui a déclenché l'événement
            **kwargs: données supplémentaires selon l'événement
        """
        pass  # par défaut : rien