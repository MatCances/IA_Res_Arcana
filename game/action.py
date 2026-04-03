from utils.constant import GameEvent


class Action:
    """Les action d'un joueur.
    Chaque action a un nom.
    Passer le tour apres chaque action
    Liste des actions possibles:
    - jouer un artefact depuis sa main en payant son cout
    - jouer le pouvoir d'une carte qui n'est pas engagée en payant son cout
    - acheter un monument en payant son cout
    - acheter un lieu de puissance en payant son cout
    - defausser une carte de sa main pour 1 gold ou 2 ressources
    - passer: echanger son objet puis piocher une carte

    Jouer autant d'actions que necessaires,
    jusqu'a ce que tout le monde ait passé
    Le premier joueur a passer prend la tuile premier joueur.
    """
    def __init__(self, name, execute):
        """
        Args:
            name (str): nom affiché de l'action
            execute (function): fonction à exécuter -> execute(state, player)
            can_execute (function, optional): condition -> can_execute(state, player)
        """
        self.name = name
        self.execute_fn = execute

    def execute(self, state, player):
        """Exécute l'action"""
        self.execute_fn(state, player)
        return True


def action_use_ability(state, player, card, ability):
    """Action : utiliser le pouvoir d'une carte"""
    def execute(state, player):
        if not player.can_afford(ability):
            print(f"Pas assez de ressources pour {ability.name}")
            return
        ability.effect(state, player)

    return Action(f"{card.name} : {ability.name}", execute)


def action_play_artifact(state, player, card):
    """Action : jouer un artefact depuis sa main"""
    def execute(state, player):
        card.play(state, player)

    return Action(f"Jouer {card.name}", execute)


def action_discard(state, player, card):
    """Action : défausser une carte"""
    def execute(state, player):
        card.discard(state, player)

    return Action(f"Défausser {card.name}", execute)

def action_buy_monument(state, player, dispatch=None):
    """Action : acheter un monument. Soit parmis les 2 disponible, soit tirer dans la pioche"""
    def execute(state, player):
        # construire les options disponibles
        options = []
        for monument in state.monuments_visible:
            options.append(monument)
        if state.monuments_deck:
            options.append(None)  # None représente "tirer dans la pioche"
        
        # construire les labels pour choose_option
        labels = [m.name for m in state.monuments_visible]
        if state.monuments_deck:
            labels.append("Tirer dans la pioche (inconnu)")
        
        choice = player.choose_option(labels, state)
        
        if options[choice] is None:
            # tirer dans la pioche
            monument = state.monuments_deck.pop(0)
            print(f"{player.name} tire {monument.name} de la pioche")
            state.logger.action(f"{player.name} tire {monument.name} de la pioche")
        else:
            # prendre un monument visible
            monument = options[choice]
            state.monuments_visible.remove(monument)
            # révéler le prochain monument
            if state.monuments_deck:
                next_monument = state.monuments_deck.pop(0)
                state.monuments_visible.append(next_monument)
                state.logger.action(f"{player.name} achète {monument.name}")
                state.logger.action(f"Monument révélé : {next_monument.name}")
        
        # payer le coût
        for resource, amount in monument.cost.items():
            player.resources.remove(resource, amount)
        
        # effet one-shot
        monument.on_buy(state, player)
        
        # ajouter au plateau
        player.board.append(monument)
        

        if dispatch:
            dispatch(GameEvent.BUY_MONUMENT, player, monument=monument)

    return Action("Acheter un monument", execute)

def action_buy_place_of_power(state, player, place, dispatch=None):
    """Action : acheter un lieu de puissance en payant son coût."""
    def execute(state, player):
        # payer le coût
        for resource, amount in place.cost.items():
            player.resources.remove(resource, amount)
        
        # ajouter le lieu au plateau du joueur
        player.board.append(place)
        
        # retirer le lieu des lieux disponibles
        state.places_of_power.remove(place)
        
        print(f"{player.name} achète {place.name}")

        if dispatch:
            dispatch(GameEvent.BUY_PLACE_OF_POWER, player, place=place)

    return Action(f"Acheter lieu de puissance {place.name}", execute)

def action_pass(state, player):
    """Action : passer le tour"""
    def execute(state, player):
        print(f"{player.name} passe son tour")

    return Action("Passer le tour", execute)