from game.action import (action_pass,
                         action_discard,
                         action_play_artifact,
                         action_use_ability,
                         action_buy_monument,
                         action_buy_monument_from_deck,
                         action_buy_place_of_power)

def choose_resource(choices):
    """Demande au joueur de choisir une ressource parmi une liste.

    Args:
        choices (list[Resource]): liste des ressources proposées

    Returns:
        Resource: la ressource choisie
    """
    for i, res in enumerate(choices):
        print(f"{i+1} - {res.value}")
    
    choice = 0
    while choice < 1 or choice > len(choices):
        try:
            choice = int(input("Numéro de la ressource : "))
        except ValueError:
            print("  ! Merci de taper un chiffre valide !")
    
    return choices[choice - 1]

def choose_card(cards):
    """Demande au joueur de choisir une carte parmi une liste.

    Args:
        cards (list[Card]): liste des cartes proposées

    Returns:
        Card: la carte choisie
    """
    for i, card in enumerate(cards):
        print(f"{i+1} - {card.name}")
    
    choice = 0
    while choice < 1 or choice > len(cards):
        try:
            choice = int(input("Numéro de la carte : "))
        except ValueError:
            print("  ! Merci de taper un chiffre valide !")
    
    return cards[choice - 1]

def choose_action(actions):
    """Affiche le menu avec toutes les actions possibles
    Attend que le joueur tape un chiffre valide
    Retourne l'action choisie

    Args:
        actions (game.Action): Actions possibles

    Returns:
        game.Action: L'action choisie
    """
    print("\n+--------------------------+")
    print("| Actions possibles :")
    for i, action in enumerate(actions):
        print(f"| {i+1} - {action.name}")
    
    choice = 0
    while choice < 1 or choice > len(actions):
        try:
            choice = int(input("| Choisis une action : "))
            if choice < 1 or choice > len(actions):
                raise ValueError
        except ValueError:
            print("  ! Merci de taper un chiffre valide !")
    return actions[choice-1]

def available_actions(state, player, dispatch=None):
    actions = []

    # utiliser le pouvoir d'une carte non engagée
    for card in player.board:
        if not card.is_tapped:
            for ability in card.get_abilities():
                if player.can_afford(ability):
                    actions.append(action_use_ability(state, player, card, ability))

    # jouer un artefact depuis la main
    for card in player.hand:
        if player.can_buy(card):
            actions.append(action_play_artifact(state, player, card))
    
    # acheter un lieu de puissance
    for place in state.places_of_power:
        if player.can_buy(place):
            actions.append(action_buy_place_of_power(state, player, place, dispatch=dispatch))

    # défausser une carte
    for card in player.hand:
        actions.append(action_discard(state, player, card))
    
    # acheter un monument visible
    for monument in state.monuments_visible:
        if player.can_buy(monument):
            actions.append(action_buy_monument(state, player, monument, dispatch=dispatch))

    # Acheter le monument sur la pioche des monuments
    if state.monuments_deck:
        actions.append(action_buy_monument_from_deck(state, player, dispatch=dispatch))
    
    # toujours disponible
    actions.append(action_pass(state, player))

    return actions