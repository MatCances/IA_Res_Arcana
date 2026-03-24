from utils.resource_pool import ResourcePool

class Player:
    """Represente un joueur
    """
    def __init__(self, name):
        self.name = name
        self.mage = None
        self.resources = ResourcePool()
        self.hand = []
        self.deck = []
        self.board = []
        self.discard = []
        self.points = 0
        self.object = None
        self.available_actions = []
    
    def set_mage(self, mage):
        self.mage = mage
    
    def can_buy(self, card):
        """Vérifie si le joueur peut payer le coût d'achat d'une carte
        (artefact, monument, lieu de pouvoir)."""
        return all(self.resources.has(r, amount) for r, amount in card.cost.items())

    def can_afford(self, ability):
        """Check si le joueur peut faire le pouvoir d'une carte

        Args:
            ability (game.ability.Ability): the ability of the card
        """
        return all(self.resources.has(r, amount) for r, amount in ability.cost.items()) 