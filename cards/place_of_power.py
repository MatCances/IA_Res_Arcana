from cards.base_card import Card
from cards.artifacts import Artifact
from utils.constant import Resource, CardType, GameEvent
from game.ability import Ability


class PlaceOfPower(Card):
    def __init__(self, name, cost):
        super().__init__(name, cost=cost)


class MysticalMenagerie(PlaceOfPower):
    def __init__(self):
        name = "Ménagerie Mystique"
        cost = {Resource.CALM: 4, Resource.LIFE: 4}
        super().__init__(name, cost)
        self.reduction_effect = {"value": 1,
                                 "excluded": [Resource.GOLD, Resource.PEARL],
                                 "card_type": [CardType.CREATURE]}
    
    def score(self, state, player):
        creatures = [c for c in player.board if c.card_type == CardType.CREATURE]
        return len(creatures) + self.resources_on.get_amount(Resource.CALM)
    
    def get_abilities(self):
        def effect1(state, player):
            untapped_creatures = [c for c in player.board if not c.is_tapped
                                 and c.card_type in [CardType.CREATURE, CardType.ILLUSIONIST]]
            chosen_creature = player.choose_card(untapped_creatures, state)
            player.resources.remove(Resource.CALM, 1)
            player.draw()
            chosen_creature.tap()
        
        def effect2(state, player):
            player.resources.remove(Resource.CALM, 7)
            self.resources_on.add(Resource.CALM, 2)
        
        def has_untapped_creature_and_deck(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if not c.is_tapped
                and c.card_type in [CardType.CREATURE, CardType.ILLUSIONIST]
                ) and bool(player.deck)
        
        abilities = [Ability(f"1 CALM et engager 1 CREATURE pour piocher une carte",
                             cost={Resource.CALM: 1},
                             effect=effect1,
                             condition=has_untapped_creature_and_deck),
                     Ability(f"7 CALM pour mettre 2 CALM sur {self.name}",
                             cost={Resource.CALM: 7},
                             effect=effect2)]
        return abilities


class SacredGrove(PlaceOfPower):
    def __init__(self):
        name = "Bosquet Sacré"
        cost = {Resource.CALM: 4, Resource.LIFE: 8}
        super().__init__(name, cost)
    
    def score(self, state, player):
        return 2 + self.resources_on.get_amount(Resource.LIFE)

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.CALM, 1)
            player.resources.add(Resource.LIFE, 5)            
            self.tap()
        
        def effect2(state, player):
            untapped_creatures = [c for c in player.board if not c.is_tapped
                                 and c.card_type in [CardType.CREATURE, CardType.ILLUSIONIST]]
            chosen_creature = player.choose_card(untapped_creatures, state)
            chosen_creature.tap()
            self.tap()
            self.resources_on.add(Resource.LIFE, 1)
        
        def has_untapped_creature(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if not c.is_tapped
                and c.card_type in [CardType.CREATURE, CardType.ILLUSIONIST]
                )
        
        abilities = [Ability(f"1 CALM pour obtenir 5 LIFE",
                             cost={Resource.CALM: 1},
                             effect=effect1),
                     Ability(f"Engager une creature pour mettre 1 LIFE sur {self.name}",
                             cost={},
                             effect=effect2,
                             condition=has_untapped_creature)]
        return abilities

class DragonsLair(PlaceOfPower):
    def __init__(self):
        name = "Repaire des Dragons"
        cost = {Resource.LIFE: 3, Resource.DEATH: 3, Resource.ELAN: 3, Resource.CALM: 3}
        super().__init__(name, cost)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.add(Resource.GOLD, 2)
            self.tap()
            print(f"{player.name} obtient 2 GOLD")
        
        def effect2(state, player):
            dragons = [card for card in player.board if not card.is_tapped and 
                      card.card_type in (CardType.DRAGON, CardType.ILLUSIONIST)]
            if not dragons:
                print("Aucun dragon disponible.")
                return
            
            print("Choisissez un dragon à engager :")
            card = player.choose_card(dragons, state)
            
            if card.card_type == CardType.ILLUSIONIST:
                print("L'Illusionniste imite un dragon : payez 2 ressources :")
                for _ in range(2):
                    resource = player.choose_resource(player.resources.available(excluded={Resource.PEARL}), state)
                    player.resources.remove(resource, 1)
            
            card.tap()
            self.resources_on.add(Resource.GOLD, 2)
            self.tap()
            print(f"2 GOLD posés sur {self.name}")
        
        def has_untapped_dragon(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if not c.is_tapped and c.card_type in [CardType.DRAGON, CardType.ILLUSIONIST]
            )
        
        return [
            Ability("2 GOLD", cost={}, effect=effect1),
            Ability("Engager un dragon pour poser 2 GOLD sur la carte",
                    cost={},
                    effect=effect2,
                    condition=has_untapped_dragon)
        ]
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.GOLD)


class DeathCatacomb(PlaceOfPower):
    def __init__(self):
        name = "Catacombes de la mort"
        cost = {Resource.DEATH: 9}
        super().__init__(name, cost)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.DEATH, 1)
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.DEATH)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.DEATH, 5)
            self.resources_on.add(Resource.DEATH, 1)            
        
        def effect2(state, player):
            self.tap()
            self.resources_on.add(Resource.DEATH, 1)
        
        abilities = [Ability(f"5 DEATH pour mettre 1 DEATH sur {self.name}",
                             cost={Resource.DEATH: 5},
                             effect=effect1),
                     Ability(f"1 DEATH sur {self.name}",
                             cost={},
                             effect=effect2)]
        return abilities


class BloodyIsland(PlaceOfPower):
    def __init__(self):
        name = "Ile Sanguinaire"
        cost = {Resource.PEARL: 1, Resource.ELAN: 4, Resource.DEATH: 4}
        super().__init__(name, cost)
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.ELAN)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.ELAN, 7)
            self.resources_on.add(Resource.ELAN, 3)            
            self.tap()
        
        def effect2(state, player):
            player.resources.remove(Resource.CALM, 1)
            player.resources.remove(Resource.DEATH, 2)
            self.resources_on.add(Resource.ELAN, 1)
        
        abilities = [Ability(f"7 ELAN pour mettre 3 ELAN sur {self.name}",
                             cost={Resource.ELAN: 7},
                             effect=effect1),
                     Ability(f"1 CALM et 2 DEATH pour mettre 1 ELAN sur {self.name}",
                             cost={Resource.CALM: 1, Resource.DEATH: 2},
                             effect=effect2)]
        return abilities


class PearlCradle(PlaceOfPower):
    def __init__(self):
        name = "Berceau de Perles"
        cost = {Resource.CALM: 6, Resource.GOLD: 3}
        super().__init__(name, cost)
    
    def score(self, state, player):
        return 2*self.resources_on.get_amout(Resource.PEARL)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.PEARL, 1)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.GOLD, 2)
            player.resources.remove(Resource.PEARL, 1)
            self.resources_on.add(Resource.PEARL, 1)            
            self.tap()
        
        def effect2(state, player):
            player.resources.remove(Resource.CALM, 4)
            player.resources.add(Resource.PEARL, 1)
            self.tap()
        
        abilities = [Ability(f"2 GOLD et 1 PEARL pour mettre 1 PEARL sur {self.name}",
                             cost={Resource.GOLD: 2, Resource.PEARL: 1},
                             effect=effect1),
                     Ability("4 CALM pour obtenir 1 PEARL",
                             cost={Resource.CALM: 4},
                             effect=effect2)]
        return abilities



class WizardBestiary(PlaceOfPower):
    def __init__(self):
        name = "Bestiaire du Sorcier"
        cost = {Resource.LIFE: 4, Resource.CALM: 2, Resource.ELAN: 2, Resource.DEATH: 2}
        super().__init__(name, cost)
    
    def score(self, state, player):
        score = 0
        for card in player.board:
            if card.card_type == CardType.CREATURE:
                score += 1
            elif card.card_type == CardType.DRAGON:
                score += 2
        return score

    def get_abilities(self):
        def effect1(state, player):
            self.tap()
            winner = state.engine.victory_check()
            if winner:
                state.engine.game_over = True
                state.engine.winner = winner
            else:
                print("Aucun joueur n'atteint 13 points, la partie continue.")
        
        def effect2(state, player):
            # récupérer tous les dragons dans toutes les défausses
            dragons = []
            for p in state.players:
                for card in p.discard:
                    if card.card_type == CardType.DRAGON:
                        dragons.append((card, p))
            
            if not dragons:
                print("Aucun dragon dans les défausses.")
                return
            
            # choisir le dragon d'abord
            print("Choisissez un dragon à récupérer :")
            cards = [card for card, _ in dragons]
            card = player.choose_card(cards, state)
            owner = next(p for c, p in dragons if c == card)

            # Nouveau cout du dragon (cout de base + 4 ANY)
            card.cost[Resource.ANY] = card.cost.get(Resource.ANY, 0) + 4
            
            # vérifier que le joueur a assez de ressources
            if not player.can_buy(card):
                print(f"Pas assez de ressources pour payer les 4 ressources et le coût de {card.name}.")
                return

            reductions = player.get_applicable_reductions(self)
            total_reduc = sum(r["value"] for r in reductions)

            fixed_cost = {r: a for r, a in card.cost.items() if r != Resource.ANY}
            any_count = card.cost.get(Resource.ANY, 0)
            total_fixed = sum(fixed_cost.values())
            fixed_to_pay = max(0, total_fixed - total_reduc)

            paid_resources = {}

            if not reductions:
                # Pas de réduction : paiement direct des ressources fixes
                for r, amount in fixed_cost.items():
                    player.resources.remove(r, amount)
                    paid_resources[r.value] = paid_resources.get(r.value, 0) + amount
            else:
                # Réduction active : le joueur choisit lesquelles payer, capé par le max du coût
                if fixed_to_pay > 0:
                    print(f"Choisissez {fixed_to_pay} ressource(s) à payer pour {card.name} :")
                    paid = {r: 0 for r in fixed_cost}
                    for _ in range(fixed_to_pay):
                        choices = [r for r, cap in fixed_cost.items()
                                if paid[r] < cap and player.resources.has(r, 1)]
                        resource = player.choose_resource(choices, state)
                        player.resources.remove(resource, 1)
                        paid[resource] += 1
                        paid_resources[resource.value] = paid_resources.get(resource.value, 0) + 1

            # Payer les slots ANY librement (PEARL), indépendamment des réductions
            if any_count > 0:
                print(f"Choisissez {any_count} ressource(s) libres à payer pour {card.name} :")
                for _ in range(any_count):
                    choices = [r for r in Resource.real()
                            if r not in {Resource.PEARL}
                            and player.resources.has(r, 1)]
                    resource = player.choose_resource(choices, state)
                    player.resources.remove(resource, 1)
                    paid_resources[resource.value] = paid_resources.get(resource.value, 0) + 1

            # retirer de la défausse et placer sur le board
            owner.discard.remove(card)
            player.board.append(card)
            print(f"{player.name} récupère {card.name} et le place sur son plateau.")
            self.tap()

        return [
            Ability("Lancer un contrôle de victoire immédiat", cost={}, effect=effect1),
            Ability("4 ressources pour récupérer un dragon d'une défausse", cost={Resource.ANY: 4}, effect=effect2,
                    condition=lambda state, _player, card: not card.is_tapped and any(
                        c for p in state.players for c in p.discard if c.card_type == CardType.DRAGON
                    ))
            ]


class AlchemistLaboratory(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Laboratoire Alchimique",
                         cost={Resource.ELAN: 3,
                               Resource.CALM: 3,
                               Resource.GOLD: 2})
    
    def score(self, state, player):
        return 2

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.CALM, 1)
            player.resources.remove(Resource.ELAN, 1)
            player.resources.remove(Resource.PEARL, 1)
            self.resources_on.add(Resource.GOLD, 2)
            self.resources_on.add(Resource.PEARL, 1)
        
        def effect2(state, player):
            player.resources.remove(Resource.ELAN, 2)
            excluded = {Resource.PEARL}
            res = player.choose_ressource(player.resources.available(excluded=excluded), state)
            player.resources.remove(res, 1)
            player.resources.add(Resource.PEARL, 1)
            self.tap()
        
        abilities = [Ability(f"1 CALM, 1 ELAN, 1 PEARL pour mettre 1 PEARL et 2 GOLD sur {self.name}",
                             cost={Resource.CALM: 1, Resource.ELAN: 1, Resource.PEARL: 1},
                             effect=effect1),
                     Ability("2 ELAN et 1 ressource au choix pour obtenir une perle",
                             cost={Resource.ELAN: 2, Resource.ANY: 1},
                             effect=effect2)]
        return abilities


class DwarfMine(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Mine des Nains",
                         cost={Resource.ELAN: 4, Resource.LIFE: 2, Resource.GOLD: 1})
    
    def collect_base(self, state, player):
        player.resources.add(Resource.GOLD, 1)
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.GOLD)

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.ELAN, 5)
            player.resources.add(Resource.GOLD, 3)
            self.tap()

        def effect2(state, player):
            player.resources.remove(Resource.DEATH, 3)
            player.resources.remove(Resource.ELAN, 3)
            self.resources_on.add(Resource.GOLD, 2)
            self.tap()
        
        abilities = [Ability(f"5 ELAN pour obtenir 3 GOLD",
                             cost={Resource.ELAN: 5},
                             effect=effect1),
                     Ability(f"3 DEATH et 3 ELAN pour mettre 2 GOLD sur {self.name}",
                             cost={Resource.ELAN: 3, Resource.DEATH: 3},
                             effect=effect2)]
        return abilities


class CursedForge(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Forge Maudite",
                         cost={Resource.ELAN: 6, Resource.DEATH: 3})
    
    def collect_base(self, state, player):
        options = ["Payer un DEATH", f"Engager {self.name}"]
        choice = player.choose_option(options, state)
        if choice == 0:
            player.resources.remove(Resource.DEATH)
        elif choice == 1:
            self.tap()
        else:
            raise ValueError("This should never happend")
    
    def score(self, state, player):
        return 1 + self.resources_on.get_amount(Resource.GOLD)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.ELAN, 2)
            player.resources.remove(Resource.GOLD, 1)
            self.resources_on.add(Resource.GOLD, 1)
    
        
        abilities = [Ability(f"2 ELAN et 1 GOLD pour mettre 1 GOLD sur {self.name}",
                             cost={Resource.ELAN: 2, Resource.GOLD: 1},
                             effect=effect1)]
        return abilities


class AlchemistTower(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Tour de l'Alchimiste",
                         cost={Resource.GOLD: 3})
        self.has_attack_reaction = True
        self.attack_reaction_requires_untapped = True
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.GOLD)

    def collect_base(self, state, player):
        choices = [r for r in Resource.real() if r not in (Resource.GOLD, Resource.PEARL)]
        for _ in range(3):
            res = player.choose_resource(choices, state)
            player.resources.add(res, 1)
    
    def on_event(self, event, state, source_player, **kwargs):
        if event == GameEvent.ATTACK and not self.is_tapped:
            owner = next(p for p in state.players if self in p.board)

            if owner.choose_yes_no(f"\n[Réaction] {owner.name} : engager {self.name} ?", state):
                self.tap()
                kwargs.get('context')['cancelled'] = True
                print(f"[Réaction] {self.name} : attaque annulée !")
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.ELAN, 1)
            player.resources.remove(Resource.CALM, 1)
            player.resources.remove(Resource.LIFE, 1)
            player.resources.remove(Resource.DEATH, 1)
            self.resources_on.add(Resource.GOLD, 1)
        
        abilities = [Ability(f"1 LIFE/CALM/ELAN/DEATH pour mettre 1 GOLD sur {self.name}",
                             cost={Resource.ELAN: 1,
                                   Resource.LIFE: 1,
                                   Resource.CALM: 1,
                                   Resource.DEATH: 1},
                             effect=effect1)]
        return abilities


class DragonsCave(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Antre de Dragon",
                         cost={Resource.ELAN: 8,
                               Resource.LIFE: 4})
    
    def collect_base(self, state, player):
        player.resources.add(Resource.GOLD, 1)
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.LIFE)

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 4)
            self.resources_on.add(Resource.LIFE, 1)

        def effect2(state, player):
            # TODO ici. Si c'est illusionnist faut payer 2 ressources (comme d'hab quand il remplace un dragon)
            untapped_dragons = [c for c in player.board if not c.is_tapped 
                                and c.card_type in [CardType.DRAGON, CardType.ILLUSIONIST]]
            chosen_dragon = player.choose_card(untapped_dragons, state)
            chosen_dragon.tap()
            self.resources_on.add(Resource.LIFE, 1)
        
        def has_untapped_dragon(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if not c.is_tapped and c.card_type in [CardType.DRAGON, CardType.ILLUSIONIST]
            )

        abilities = [Ability(f"4 LIFE pour mettre 1 LIFE sur {self.name}",
                             cost={Resource.LIFE: 4},
                             effect=effect1),
                     Ability(f"Engager un DRAGON pour mettre 1 LIFE sur {self.name}",
                             cost={},
                             effect=effect2,
                             condition=has_untapped_dragon)]
        return abilities


class CrystalFortress(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Forteresse de Cristal",
                         cost={Resource.ELAN: 4,
                               Resource.LIFE: 4,
                               Resource.CALM: 4,
                               Resource.DEATH: 4,
                               Resource.GOLD: 4})
    
    def score(self, state, player):
        on_board_artefacts = [c for c in player.board if isinstance(c, Artifact)]
        return 5 + len(on_board_artefacts) // 2
    
    def get_abilities(self):
        def effect1(state, player):
            self.tap()
            winner = state.engine.victory_check()
            if winner:
                state.engine.game_over = True
                state.engine.winner = winner
            else:
                print("Aucun joueur n'atteint 13 points, la partie continue.")

        return [Ability("Lancer un contrôle de victoire immédiat",
                        cost={},
                        effect=effect1)]


class HellDoor(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Porte des Enfers",
                         cost={Resource.ELAN: 6,
                               Resource.DEATH: 3})
    
    def score(self, state, player):
        on_board_demons = [c for c in player.board if c.card_type is CardType.DEMON]
        return len(on_board_demons) + self.resources_on.get_amount(Resource.DEATH)
    
    def get_abilities(self):
        def effect1(state, player):
            untapped_demons = [c for c in player.board
                               if not c.is_tapped
                               and c.card_type in [CardType.DEMON, CardType.ILLUSIONIST]]
            chosen_demon = player.choose_card(untapped_demons, state)
            chosen_demon.tap()
            self.tap()
            self.resources_on.add(Resource.DEATH, 1)

        def effect2(state, player):
            creatures = [c for c in player.board
                         if c.card_type == CardType.CREATURE]
            chosen_creature = player.choose_card(creatures, state)
            player.board.remove(chosen_creature)
            player.discard.append(chosen_creature)
            self.resources_on.add(Resource.DEATH, 1)
        
        def effect3(state, player):
            player.resources.remove(Resource.ELAN, 4)
            self.resources_on.add(Resource.DEATH, 1)
        
        def has_untapped_demon(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if not c.is_tapped and c.card_type in [CardType.DEMON, CardType.ILLUSIONIST]
            )
        
        def has_creature(_s, player, card):
            return not card.is_tapped and any(c for c in player.board if c.card_type == CardType.CREATURE)

        abilities = [Ability(f"Engager 1 DEMON et {self.name} pour mettre 1 DEATH sur {self.name}",
                             cost={},
                             effect=effect1,
                             condition=has_untapped_demon),
                     Ability(f"Détruisez une crature pour mettre 1 DEATH sur {self.name}",
                             cost={},
                             effect=effect2,
                             condition=has_creature),
                     Ability(f"4 ELAN pour mettre 1 DEATH sur {self.name}",
                             cost={Resource.ELAN: 4},
                             effect=effect3)]
        return abilities


class AbyssalTemple(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Temple des Abysses",
                         cost={Resource.CALM: 6,
                               Resource.DEATH: 3})
    
    def score(self, state, player):
        return self.resources_on.get_amount(Resource.CALM)
    
    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 2)
            for p in state.players:
                tapped_demons = [c for c in p.board if c.is_tapped and c.card_type is CardType.DEMON]
                for demon in tapped_demons:
                    demon.untap()
            self.tap()

        def effect2(state, player):
            player.resources.remove(Resource.CALM, 2)
            player.resources.remove(Resource.DEATH, 2)
            self.resources_on.add(Resource.CALM, 1)

        def effect3(state, player):
            untapped_demons = [c for c in player.board
                               if not c.is_tapped
                               and c.card_type in [CardType.DEMON, CardType.ILLUSIONIST]]
            chosen_demon = player.choose_card(untapped_demons, state)
            chosen_demon.tap()
            self.resources_on.add(Resource.CALM, 1)
        
        def has_untapped_demon(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if not c.is_tapped and c.card_type in [CardType.DEMON, CardType.ILLUSIONIST]
            )
        
        def has_tapped_demon(_s, player, card):
            return not card.is_tapped and any(c for c in player.board if c.is_tapped and c.card_type is CardType.DEMON)

        abilities = [Ability(f"2 LIFE pour revive tous les demons",
                             cost={Resource.LIFE: 2},
                             effect=effect1,
                             condition=has_tapped_demon),
                     Ability(f"2 CALM et 2 DEATH pour mettre 1 CALM sur {self.name}",
                             cost={Resource.CALM: 2, Resource.DEATH: 2},
                             effect=effect2),
                     Ability(f"Engagez un démon pour mettre 1 CALM sur {self.name}",
                             cost={},
                             effect=effect3,
                             condition=has_untapped_demon)]
        return abilities


class SacrificialPit(PlaceOfPower):
    def __init__(self):
        super().__init__(name="Puits Sacrificiel",
                         cost={Resource.ELAN: 8,
                               Resource.DEATH: 4})
    
    def score(self, state, player):
        return 2 + self.resources_on.get_amount(Resource.DEATH)

    def get_abilities(self):
        def effect1(state, player):
            player.resources.remove(Resource.LIFE, 3)
            self.resources_on.add(Resource.DEATH, 1)
            self.tap()

        def effect2(state, player):
            drags_or_creas = [c for c in player.board
                              if c.card_type in [CardType.CREATURE, CardType.DRAGON]]
            chosen = player.choose_card(drags_or_creas, state)
            total_cost = sum(val for _, val in chosen.cost.items())

            player.resources.add(Resource.GOLD, total_cost)
            player.resources.remove(Resource.DEATH, 1)
            self.tap()
        
        def has_drag_or_crea(_s, player, card):
            return not card.is_tapped and any(
                c for c in player.board if c.card_type in [CardType.CREATURE, CardType.DRAGON]
            )

        abilities = [Ability(f"3 LIFE pour mettre 1 DEATH sur {self.name}",
                             cost={Resource.LIFE: 3},
                             effect=effect1),
                     Ability(f"1 DEATH et détruisez 1 DRAGON/CREATURE: Gagnez son cout en GOLD",
                             cost={Resource.DEATH: 1},
                             effect=effect2,
                             condition=has_drag_or_crea)]
        return abilities


ALL_PLACES_OF_POWER = [MysticalMenagerie(),
                       SacredGrove(),
                       DragonsLair(),
                       DeathCatacomb(),
                       BloodyIsland(),
                       WizardBestiary(),
                       AbyssalTemple(),
                       HellDoor(),
                       CrystalFortress(),
                       DragonsCave(),
                       AlchemistTower(),
                       AlchemistLaboratory(),
                       CursedForge(),
                       DwarfMine(),
                       SacrificialPit(),
                       PearlCradle()
                       ]