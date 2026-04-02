from game.player import Player

class HumanPlayer(Player):

    def choose_card(self, choices):
        for i, card in enumerate(choices):
            print(f"{i+1} - {card.name}")
        choice = 0
        while choice < 1 or choice > len(choices):
            try:
                choice = int(input("Numéro de la carte : "))
            except ValueError:
                print("  ! Merci de taper un chiffre valide !")
        return choices[choice - 1]

    def choose_resource(self, choices):
        for i, res in enumerate(choices):
            print(f"{i+1} - {res.value}")
        choice = 0
        while choice < 1 or choice > len(choices):
            try:
                choice = int(input("Numéro de la ressource : "))
            except ValueError:
                print("  ! Merci de taper un chiffre valide !")
        return choices[choice - 1]

    def choose_action(self, actions):
        print("\n+--------------------------+")
        print("| Actions possibles :")
        for i, action in enumerate(actions):
            print(f"| {i+1} - {action.name}")
        choice = 0
        while choice < 1 or choice > len(actions):
            try:
                choice = int(input("| Choisis une action : "))
            except ValueError:
                print("  ! Merci de taper un chiffre valide !")
        return actions[choice - 1]
    
    def choose_option(self, options):
        for i, option in enumerate(options):
            print(f"{i+1} - {option}")
        choice = 0
        while choice < 1 or choice > len(options):
            try:
                choice = int(input("Votre choix : "))
            except ValueError:
                print("  ! Merci de taper un chiffre valide !")
        return choice - 1
    
    def choose_yes_no(self, question):
        """Renvoie True si le choix est 1 - Oui, False sinon.
        La fonction commence comme ca:

        print(question)
        print("1 - Oui")
        print("2 - Non")
    
        Args:
            question (str): La question

        Returns:
            _type_: _description_
        """
        print(question)
        print("1 - Oui")
        print("2 - Non")
        choice = 0
        while choice not in [1, 2]:
            try:
                choice = int(input("Votre choix : "))
            except ValueError:
                pass
        return choice == 1