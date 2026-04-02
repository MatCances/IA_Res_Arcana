import random
from game.player import Player

class AIPlayer(Player):

    def choose_card(self, choices):
        return random.choice(choices)

    def choose_resource(self, choices):
        return random.choice(choices)

    def choose_action(self, actions):
        return random.choice(actions)
    
    def choose_option(self, options):
        return random.randint(0, len(options) - 1)

    def choose_yes_no(self, question):
        return random.choice([True, False])
    
    def choose_number(self, min_val, max_val):
        return random.randint(min_val, max_val)