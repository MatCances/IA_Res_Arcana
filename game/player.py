from utils.resource_pool import ResourcePool
from utils.constant import Resource
from itertools import combinations_with_replacement

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
        # bonus points pour les points additionnel de réaction
        self.bonus_points = 0
    
    def set_mage(self, mage):
        self.mage = mage
    
    def get_applicable_reductions(self, card):
        """Recupère toutes les réduction qui s'applique à une carte"""
        total_reduction = []

        for board_card in self.board:
            reduction_effect = board_card.reduction_effect
            if reduction_effect:
                if card.card_type in reduction_effect["card_type"]:
                    total_reduction.append({"value": reduction_effect["value"],
                                            "excluded": reduction_effect["excluded"]})            

        return total_reduction
        
    def can_buy(self, card):
        """Vérifie si le joueur peut payer le coût d'achat d'une carte,
        aussi en fonction du cout réduit s'il y a.
        (artefact, monument, lieu de pouvoir)."""

        reductions = self.get_applicable_reductions(card)
        if not reductions:
            return all(self.resources.has(r, amount)
                    for r, amount in card.cost.items())

        # Jamais une carte ne peut réduire le cout en perle
        all_resources = [Resource.CALM,
                         Resource.DEATH,
                         Resource.LIFE,
                         Resource.ELAN,
                         Resource.GOLD]

        # Générer les ressources qu'on peut réduire
        # ca gère les doublons ça c'est bon
        available_resources = []
        for reduction in reductions:
            for r in all_resources:
                if r not in reduction["excluded"]:
                    available_resources.append(r)
        
        # cout total des reductions parmis la liste available_resources
        total_reduction = sum(r['value'] for r in reductions)

        # Test sur tous les combi possibles
        for reduction_combo in combinations_with_replacement(available_resources, total_reduction):
            test_cost = card.cost.copy()

            # Applique la reduc
            for resource in reduction_combo:
                if test_cost.get(resource, 0) > 0:
                    test_cost[resource] -= 1
            
            # Verifie si le joueur peut payer maintenant
            if all(self.resources.has(r, amount)
                   for r, amount in test_cost.items()):
                return True
        
        return False

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
        
        # Ajout des perles sur les cartes
        pearl_on_cards = sum([c.resources_on.get_amount(Resource.PEARL)
                              for c in self.board])
        score += pearl_on_cards
        
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

    # --- Méthodes de décision ---
    # Ces méthodes sont à implémenter dans HumanPlayer et AIPlayer.
    # Elles représentent tous les moments où on demande quelque chose à un joueur.
    # Le parametre state sert uniquement pour le logger dans ces fonction
 
    def choose_card(self, choices, state=None):
        """Choisir une carte parmi une liste."""
        raise NotImplementedError
 
    def choose_resource(self, choices, state=None):
        """Choisir une ressource parmi une liste."""
        raise NotImplementedError
 
    def choose_action(self, actions, state=None):
        """Choisir une action parmi la liste des actions disponibles."""
        raise NotImplementedError

    def choose_option(self, options, state=None):
        """Choisir parmi une liste d'options textuelles.
        """
        raise NotImplementedError
    
    def choose_yes_no(self, question, state=None):
        """Choisir oui ou non.
        
        Returns:
            bool: True si oui, False si non
        """
        raise NotImplementedError
    
    def choose_number(self, min_val, max_val, state=None):
        raise NotImplementedError