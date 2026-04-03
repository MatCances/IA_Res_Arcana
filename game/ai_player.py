import random
from game.player import Player

class AIPlayer(Player):

    def choose_card(self, choices, state=None):
        return random.choice(choices)

    def choose_resource(self, choices, state=None):
        return random.choice(choices)

    def choose_action(self, actions, state=None):
        return random.choice(actions)
    
    def choose_option(self, options, state=None):
        return random.randint(0, len(options) - 1)

    def choose_yes_no(self, question, state=None):
        return random.choice([True, False])
    
    def choose_number(self, min_val, max_val, state=None):
        return random.randint(min_val, max_val)