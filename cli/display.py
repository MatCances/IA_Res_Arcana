def display_state(state):
    print(f"\n+===== MANCHE {state.turn} =====")
    for player in state.players:
        print(f"\n+------------ {player.name} | {player.points} pts ------------+")
        print(f"| Mage : {player.mage.name} ({'engagé' if player.mage.is_tapped else 'disponible'})")
        print(f"| Objet : {player.object.name if player.object else 'aucun'}")
        print(f"| Ressources : {player.resources}")
        print(f"| Pioche : {len(player.deck)}")

        # cartes en main
        if player.hand:
            print("| Main :")
            for card in player.hand:
                print(f"|   - {card.name}")
        else:
            print("| Main : vide")

        # cartes sur le plateau
        if player.board:
            print("| Plateau :")
            for card in player.board:
                status = "engagée" if card.is_tapped else "disponible"
                stored = {r: a for r, a in card.resources_on.resources.items() if a > 0}
                stored_str = ""
                if stored:
                    stored_str = " | sur la carte : " + ", ".join(f"{a} {r.value}" for r, a in stored.items())
                print(f"|   - {card.name} ({status}){stored_str}")
        else:
            print("| Plateau : vide")
        
        # carte de la défausse
        if player.discard:
            print("| Défausse :")
            for card in player.discard:
                print(f"|   - {card.name}")
        else:
            print("| Défausse : vide")
        print(f"+--------------------------------------+")

    print(f"+--------------------------------------+")
    print(f"| Monuments disponibles: (pioche: {len(state.monuments_deck)})")
    for m in state.monuments_visible:
        print(f"|   - {m.name}")
    print(f"| Lieux de puissance disponibles:")
    for pp in state.places_of_power:
        print(f"|   - {pp.name}")
    print(f"+--------------------------------------+")
