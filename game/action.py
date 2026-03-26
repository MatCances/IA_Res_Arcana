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


def action_buy_monument(state, player, monument, dispatch=None):
    """Action : acheter un monument en payant son coût."""
    def execute(state, player):
        # payer le coût
        for resource, amount in monument.cost.items():
            player.resources.remove(resource, amount)
        
        # effet one-shot
        monument.on_buy(state, player)
        
        # ajouter le monument au plateau du joueur
        player.board.append(monument)
        
        # retirer le monument des monuments disponibles
        state.monuments_visible.remove(monument)

        # Réveler le prochain monument
        state._reveal_next_monument()
        
        print(f"{player.name} achète {monument.name}")

        if dispatch:
            dispatch(GameEvent.BUY_MONUMENT, player, monument=monument)

    return Action(f"Acheter {monument.name}", execute)

def action_buy_monument_from_deck(state, player, dispatch=None):
    """Action : tirer et acheter le premier monument de la pioche."""
    def execute(state, player):
        if not state.monuments_deck:
            print("Aucun monument dans la pioche !")
            return

        # Tirer le premier monument de la pioche
        monument = state.monuments_deck.pop(0)
        print(f"{player.name} tire et achète {monument.name} de la pioche")
        
        # payer le coût
        for resource, amount in monument.cost.items():
            player.resources.remove(resource, amount)
        
        # effet one-shot
        monument.on_buy(state, player)
        
        # ajouter le monument au plateau du joueur
        player.board.append(monument)

        if dispatch:
            dispatch(GameEvent.BUY_MONUMENT, player, monument=monument)

    return Action(f"Tirer un monument de la pioche", execute)

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