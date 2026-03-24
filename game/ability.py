class Ability:
    """Class qui gère les pouvoirs des cartes
    """
    def __init__(self, name, cost, effect=None):
        """_summary_

        Args:
            name (str): le nom du pouvoir de la carte
            cost (dict): son cout
        """
        self.name = name
        self.cost = cost
        self.effect = effect  # function (state, player) -> None
    
    def execute(self, state, player):
        if self.effect:
            self.effect(state, player)