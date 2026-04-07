import random as rd
from cards.monuments import Monument
from game.game_state import GameState
from cli.display import display_state
from utils.constant import Resource, GameEvent
from game.action import (action_pass,
                         action_discard,
                         action_play_artifact,
                         action_use_ability,
                         action_buy_monument,
                         action_buy_place_of_power)
from utils.logger import Logger


WINNING_SCORE = 13

class Engine:
    def __init__(self,
                 players,
                 mages,
                 artifacts,
                 monuments,
                 places_of_power,
                 objects,
                 scrolls,
                 logger=None):
        self.logger = logger or Logger(level=0)  # silencieux par défaut
        self.state = GameState(players)
        self.state.engine = self
        self.available_mages = mages
        self.available_artifacts = artifacts
        self.available_monuments = monuments
        self.available_places_of_power = places_of_power
        self.available_objects = objects
        self.available_scrolls = scrolls
        self.game_over = False
        self.winner = None
        self.first_player_tile = None

        # Dans l'état du jeu, tous les objet et parchemin sont pris
        # Contrairement aux monuments/lieu de puissance (voir setup_board)
        self.state.objects = objects
        self.state.scrolls = scrolls
        self.state.logger = self.logger
    
    def setup(self):
        self._give_starting_resources()
        self._setup_board()
        self._deal_mage_choices()
        self._draft_phase()
        self._choose_first_player()
        self._draw_starting_hand()
        self._choose_mages()
        self._choose_objects()
    
    def _give_starting_resources(self):
        for player in self.state.players:
            for resource in Resource.real():
                player.resources.add(resource, 11)
    
    def _setup_board(self):
        self.state.places_of_power = rd.sample(self.available_places_of_power, 4)
        monuments_pool = rd.sample(self.available_monuments, 7)
        # Les 2 premier monuments face visibles
        self.state.monuments_visible = monuments_pool[:2]
        self.state.monuments_deck = monuments_pool[2:]
        places = [p.name for p in self.state.places_of_power]
        monuments = [m.name for m in self.state.monuments_visible]
        self.logger.action(
            f"Mise en place — lieux: {places} | monuments visibles: {monuments}",
            data={"places_of_power": places, "monuments_visible": monuments}
        )
    
    def _deal_mage_choices(self):
        mage_pool = rd.sample(self.available_mages, len(self.state.players) * 2)
        for i, player in enumerate(self.state.players):
            player.mage_choices = mage_pool[i * 2 : i * 2 + 2]
            choices = [m.name for m in player.mage_choices]
            self.logger.action(
                f"{player.name} — mages proposés: {choices}",
                data={"player": player.name, "mage_choices": choices}
            )

    def _draft_phase(self):
        """Draft : 2 tours de 4 cartes, chaque joueur choisit 1 carte et passe les autres."""
        for draft_round in range(2):
            self.logger.action(f"Draft — tour {draft_round + 1}")
            # distribuer 4 cartes à chaque joueur
            hands = []
            for player in self.state.players:
                hand = rd.sample(self.available_artifacts, 4)
                for card in hand:
                    self.available_artifacts.remove(card)
                hands.append(hand)

            # chaque joueur choisit 1 carte et passe les autres
            for _ in range(4):
                new_hands = [[] for _ in self.state.players]
                for idx, player in enumerate(self.state.players):
                    hand = hands[idx]
                    if not hand:
                        continue

                    print(f"\n{player.name}, choisissez une carte :")
                    chosen = player.choose_card(hand)
                    hand.remove(chosen)
                    player.hand.append(chosen)
                    self.logger.action(
                        f"{player.name} draft {chosen.name}",
                        data={"player": player.name, "card": chosen.name}
                    )

                    # passe les cartes restantes au joueur suivant
                    next_idx = (idx + 1) % len(self.state.players)
                    new_hands[next_idx].extend(hand)
                hands = new_hands
    
    def _choose_first_player(self):
        self.state.current_player = rd.randint(0, len(self.state.players) - 1)
        first = self.state.players[self.state.current_player]
        self.logger.action(
            f"Premier joueur : {first.name}",
            data={"first_player": first.name}
        )

    def _draw_starting_hand(self):
        """Chaque joueur pioche 3 cartes depuis sa main de draft."""
        for player in self.state.players:
            drawn = rd.sample(player.hand, min(3, len(player.hand)))
            for card in drawn:
                player.hand.remove(card)
            player.deck = player.hand   # les cartes restantes vont dans la pioche
            player.hand = drawn
            hand_names = [c.name for c in player.hand]
            self.logger.action(
                f"{player.name} pioche sa main de départ : {hand_names}",
                data={"player": player.name, "starting_hand": hand_names}
            )

    def _choose_mages(self):
        for player in self.state.players:
            print(f"\n{player.name}, choisissez votre mage :")
            chosen_mage = player.choose_card(player.mage_choices)
            player.set_mage(chosen_mage)
            player.board.append(chosen_mage)
            self.logger.action(
                f"{player.name} choisit le mage {chosen_mage.name}",
                data={"player": player.name, "mage": chosen_mage.name}
            )
    
    def _choose_objects(self):
        """Choix des objets en sens antihoraire en commençant par le dernier joueur."""
        n = len(self.state.players)
        order = [(self.state.current_player - 1 - i) % n for i in range(n)]
        for idx in order:
            player = self.state.players[idx]
            print(f"\n{player.name}, choisissez un objet :")
            chosen = player.choose_card(self.state.objects)
            self.state.objects.remove(chosen)
            player.object = chosen
            player.board.append(chosen)
            self.logger.action(
                f"{player.name} choisit l'objet {chosen.name}",
                data={"player": player.name, "object": chosen.name}
            )
    
    def dispatch_event(self, event, source_player, **kwargs):
        """Notifie toutes les cartes en jeu d'un événement.
        
        Args:
            event (GameEvent): l'événement déclenché
            source_player (Player): le joueur à l'origine de l'événement
            **kwargs: données supplémentaires selon l'événement
        """
        for player in self.state.players:
            for card in player.board:
                card.on_event(event, self.state, source_player, **kwargs)
    
    def resolve_attack(self, target, damage):
        self.logger.action(
            f"Attaque — {target.name} reçoit {damage} dégâts",
            data={"target": target.name, "damage": damage}
        )
        
        attack_context = {
            "damage": damage,
            "cancelled": False
        }
        
        # 1. les cartes de réaction disponibles
        reaction_cards = [card for card in target.board if not card.is_tapped]
        
        # 2. proposer au joueur de payer ou d'utiliser une carte
        print(f"\n{target.name}, comment voulez-vous résoudre l'attaque ?")
        print(f"1 - Payer les dégâts ({damage} LIFE, ou 2 ressources par LIFE manquant)")
        for i, card in enumerate(reaction_cards):
            print(f"{i+2} - Utiliser {card.name}")
        
        choice = 0
        while choice < 1 or choice > 1 + len(reaction_cards):
            try:
                choice = int(input("Votre choix : "))
            except ValueError:
                pass
        
        # 3. si le joueur utilise une carte de réaction
        if choice > 1:
            card = reaction_cards[choice - 2]
            card.on_event(GameEvent.ATTACK, self.state, target, context=attack_context)
            if attack_context["cancelled"]:
                self.logger.action(
                    f"{target.name} esquive l'attaque",
                    data={"target": target.name}
                )
                return
        
        # 4. absorber les dégâts avec des LIFE
        damage = attack_context["damage"]
        life_available = target.resources.resources[Resource.LIFE]
        life_paid = min(life_available, damage)
        target.resources.remove(Resource.LIFE, life_paid)
        remaining = damage - life_paid
        
        # 5. pour chaque LIFE manquant, payer 2 ressources
        for _ in range(remaining):
            print(f"{target.name} n'a pas assez de LIFE, choisissez 2 ressources :")
            for _ in range(2):
                available = target.resources.available()
                if not available:
                    print("Plus aucune ressource disponible !")
                    break
                resource = target.choose_resource(available)
                target.resources.remove(resource, 1)

    def collect_phase(self):
        """Étape 1 : collecte fixe puis collecte des ressources posées sur les cartes."""
        self.logger.action(f"--- Phase de collecte (manche {self.state.turn}) ---")
        for player in self.state.players:
            self.logger.state(
                f"{player.name} — ressources avant collecte : {player.resources}",
                data={"player": player.name, "resources": dict(player.resources.resources)}
            )

            # collecte des ressources posées sur les cartes (tout ou rien)
            for card in player.board:
                stored = {r: a for r, a in card.resources_on.resources.items() if a > 0}
                if not stored:
                    continue
                print(f"\n{card.name} a des ressources posées dessus :")
                for r, a in stored.items():
                    print(f"  - {a} {r.value}")
                choice = ""
                while choice not in ["1", "2"]:
                    print("1 - Tout prendre")
                    print("2 - Tout laisser")
                    choice = input("Votre choix : ")
                if choice == "1":
                    for r, a in stored.items():
                        player.resources.add(r, a)
                        card.resources_on.remove(r, a)
                    self.logger.action(
                        f"{player.name} récupère les ressources de {card.name} : {stored}",
                        data={"player": player.name, "card": card.name,
                              "resources_taken": {r.value: a for r, a in stored.items()}}
                    )
        
            # collecte fixe de toutes les cartes
            for card in player.board:
                card.collect_base(self.state, player)
    
    def available_actions(self, player):
        """Determine les actions disponible pour le joueur player

        Args:
            player (Player): le joueur

        Returns:
            List[Action()]: la liste des actions
        """
        actions = []

        # utiliser le pouvoir d'une carte
        for card in player.board:
            for ability in card.get_abilities():
                if player.can_afford(ability) and ability.condition(self.state, player, card):
                    actions.append(action_use_ability(self.state, player, card, ability))

        # jouer un artefact depuis la main
        for card in player.hand:
            if player.can_buy(card):
                actions.append(action_play_artifact(self.state, player, card))
        
        # acheter un lieu de puissance
        for place in self.state.places_of_power:
            if player.can_buy(place):
                actions.append(action_buy_place_of_power(self.state, player, place, dispatch=self.dispatch_event))

        # défausser une carte
        for card in player.hand:
            actions.append(action_discard(self.state, player, card))
        
        # Achter un monument visible ou en tirant dans la pioche
        if self.state.monuments_visible or self.state.monuments_deck:
            if player.can_buy(Monument("Any")):
                actions.append(action_buy_monument(self.state, player, dispatch=self.dispatch_event))
        
        # toujours disponible
        actions.append(action_pass(self.state, player))

        return actions
    
    def action_phase(self):
        """Étape 2 : les joueurs jouent chacun leur tour jusqu'à ce que tout le monde passe."""
        self.logger.action(f"--- Phase d'actions (manche {self.state.turn}) ---")
        passed = {player: False for player in self.state.players}
        first_to_pass = None

        while not all(passed.values()):
            for player in self._get_play_order():
                if passed[player]:
                    continue

                if self.game_over:
                    return

                display_state(self.state)
                self.logger.state(
                    f"Tour de {player.name} — ressources : {player.resources}",
                    data={"player": player.name, "resources": dict(player.resources.resources)}
                )

                actions = self.available_actions(player)
                action = player.choose_action(actions)

                self.logger.action(
                    f"{player.name} joue : {action.name}",
                    data={"player": player.name, "action": action.name}
                )

                action.execute(self.state, player)

                if action.name == "Passer le tour":
                    passed[player] = True

                    # premier à passer : prend la tuile 1er joueur
                    if first_to_pass is None:
                        first_to_pass = player
                        self.first_player_tile = player
                        self.logger.action(
                            f"{player.name} prend la tuile 1er joueur",
                            data={"player": player.name}
                        )

                    # échange son objet
                    self._exchange_object(player)

                    # pioche une carte
                    self._draw_card(player)

                    # si tous les autres ont aussi passé, on arrête
                    if all(passed.values()):
                        break

        # le prochain 1er joueur est celui qui a pris la tuile
        self.state.current_player = self.state.players.index(self.first_player_tile)
    
    def _get_play_order(self):
        """Retourne les joueurs dans l'ordre à partir du joueur courant."""
        n = len(self.state.players)
        return [self.state.players[(self.state.current_player + i) % n] for i in range(n)]

    def _exchange_object(self, player):
        """Le joueur échange son objet avec un disponible sur le plateau."""

        if not self.state.objects:
            self.logger.action(f"{player.name} — aucun objet disponible à l'échange")
            return

        print(f"\n{player.name}, échangez votre objet ({player.object.name}) :")
        old_object = player.object
        chosen = player.choose_card(self.state.objects)
        self.state.objects.remove(chosen)

        player.object = chosen
        player.board.append(player.object)
        self.state.objects.append(old_object)
        self.logger.action(
            f"{player.name} échange {old_object.name} contre {chosen.name}",
            data={"player": player.name, "old_object": old_object.name, "new_object": chosen.name}
        )

    def _draw_card(self, player):
        """Le joueur pioche une carte de sa pioche."""
        if not player.deck:
            self.logger.action(f"{player.name} — pioche vide", data={"player": player.name})
            return
        card = player.deck.pop(0)
        player.hand.append(card)
        self.logger.action(
            f"{player.name} pioche {card.name}",
            data={"player": player.name, "card": card.name}
        )
    
    def victory_check(self):
        """Étape 3 : vérifie si un joueur a atteint 13 points."""
        self.dispatch_event(GameEvent.VICTORY_CHECK, None)

        scores = {p.name: p.points for p in self.state.players}
        self.logger.action(
            f"Contrôle de victoire — scores : {scores}",
            data={"scores": scores}
        )

        max_score = max(p.points for p in self.state.players)

        if max_score < WINNING_SCORE:
            for p in self.state.players:
                p.bonus_points = 0
            return None

        winners = [p for p in self.state.players if p.points == max_score]

        if len(winners) > 1:
            self.logger.action("Égalité — match nul", data={"result": "draw", "scores": scores})
            return "draw"

        winner = winners[0]
        self.logger.action(
            f"{winner.name} gagne la partie !",
            data={"winner": winner.name, "score": winner.points}
        )
        return winner

    def untap_all(self):
        """Désengage toutes les cartes de tous les joueurs."""
        for player in self.state.players:
            for card in player.board:
                card.untap()
    
    def run(self):
        self.setup()
        while True:
            self.logger.set_turn(self.state.turn)
            self.logger.action(f"====== Manche {self.state.turn} ======")
            self.collect_phase()
            self.action_phase()
            if self.game_over:
                break
            self.untap_all()
            winner = self.victory_check()
            if winner:
                break
            self.state.turn += 1