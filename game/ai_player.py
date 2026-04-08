import random
from game.player import Player

class AIPlayer(Player):

    def choose_card(self, choices, state=None):
        chosen = random.choice(choices)
        if state:
            state.logger.decision(f"{self.name}.choose_card([{', '.join(c.name for c in choices)}]) → {chosen.name}")
        return chosen

    def choose_resource(self, choices, state=None):
        chosen = random.choice(choices)
        if state:
            state.logger.decision(f"{self.name}.choose_resource([{', '.join(c.value for c in choices)}]) → {chosen.value}")
        return chosen

    def choose_action(self, actions, state=None):
        chosen = random.choice(actions)
        if state:
            state.logger.decision(f"{self.name}.choose_action([{', '.join(a.name for a in actions)}]) → {chosen.name}")
        return chosen
    
    def choose_option(self, options, state=None):
        chosen = random.randint(0, len(options) - 1)
        if state:
            state.logger.decision(f"{self.name}.choose_option([{', '.join(op for op in options)}]) → {options[chosen]}")
        return chosen

    def choose_yes_no(self, question, state=None):
        chosen = random.choice([True, False])
        if state:
            state.logger.decision(f"{self.name}.choose_yes_no([{question}]) → {chosen}")
        return chosen
    
    def choose_number(self, min_val, max_val, state=None):
        chosen = random.randint(min_val, max_val)
        if state:
            state.logger.decision(f"{self.name}.choose_number([{', '.join(str(n) for n in range(min_val, max_val+1))}]) → {chosen}")
        return chosen