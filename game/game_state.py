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
        self.places_of_power = None
        self.monuments_visible = None
        self.monuments_deck = None
    
    def next_player(self):
        """passe au joueur suivant de facon circulaire
        """
        self.current_player = (self.current_player + 1) % len(self.players)

    def _reveal_next_monument(self):
        """Remplit la liste des visibles avec la pioche si nécessaire."""
        while len(self.monuments_visible) < 2 and self.monuments_deck:
            monument = self.monuments_deck.pop(0)
            self.monuments_visible.append(monument)
            print(f"Monument révélé : {monument.name}")

    def clone(self):
        raise NotImplementedError("clone() est requis pour l'IA")

    def is_terminal(self):
        raise NotImplementedError

    def get_winner(self):
        raise NotImplementedError