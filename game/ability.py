class Ability:
    """Class qui gère les pouvoirs des cartes
    """
    def __init__(self, name, cost, effect=None,
                 condition=lambda _state, _player, card: not card.is_tapped):
        """
        Args:
            name (str): le nom du pouvoir de la carte
            cost (dict): son cout
            effect (function): function (state, player) -> None
            condition (function): function (state, player, card) -> bool.
                Par défaut : True si la carte n'est pas engagée.
                Surcharger pour les cas particuliers (ex: Molosse qui s'active engagé).
        """
        self.name = name
        self.cost = cost
        self.effect = effect
        self.condition = condition

    def execute(self, state, player):
        if self.effect:
            self.effect(state, player)
