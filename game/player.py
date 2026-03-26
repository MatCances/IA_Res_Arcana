from utils.resource_pool import ResourcePool
from utils.constant import Resource
from cli.input_handler import choose_resource

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
        self.object = None
        self.available_actions = []
        # bonus points pour les points additionnel de réaction
        self.bonus_points = 0
    
    def set_mage(self, mage):
        self.mage = mage
    
    def can_buy(self, card):
        """Vérifie si le joueur peut payer le coût d'achat d'une carte
        (artefact, monument, lieu de pouvoir)."""
        return all(self.resources.has(r, amount)
                   for r, amount in card.cost.items())

    def can_afford(self, ability):
        """Check si le joueur peut faire le pouvoir d'une carte

        Args:
            ability (game.ability.Ability): the ability of the card
        """
        return all(self.resources.has(r, amount)
                   for r, amount in ability.cost.items())
    
    @property
    def points(self):
        """Le score du joueur (calculé à chaque accès).
        
        Returns:
            int: Score total (perles + cartes)
        """
        score = 0
        
        # Points des perles
        pearl_count = self.resources.resources[Resource.PEARL]
        if isinstance(pearl_count, (int, float)):
            score += pearl_count
        
        # Points des cartes
        for card in self.board:
            try:
                if hasattr(card, 'score') and callable(card.score):
                    card_score = card.score(None, self)
                    if isinstance(card_score, (int, float)):
                        score += card_score
            except Exception as e:
                print(f"⚠️ Erreur dans score de {card.name}: {e}")
        
        return int(score) + self.bonus_points