class GameState:
    """Represente l'etat global de la partie
    """
    def __init__(self, players):
        """_summary_

        Args:
            players (List of Game.Player): all the players
        """
        self.players = players
        self.turn = 1
        self.current_player = 0
        self.engine = None
    
    def next_player(self):
        """passe au joueur suivant de facon circulaire
        """
        self.current_player = (self.current_player + 1) % len(self.players)

    def clone(self):
        raise NotImplementedError("clone() est requis pour l'IA")

    def is_terminal(self):
        raise NotImplementedError

    def get_winner(self):
        raise NotImplementedError