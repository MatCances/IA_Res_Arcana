from cards.base_card import Card
from utils.constant import Resource, CardType
from game.ability import Ability


class PlaceOfPower(Card):
    def __init__(self, name, cost):
        super().__init__(name, cost=cost)


class MysticalMenagerie(PlaceOfPower):
    def __init__(self):
        name = "Ménagerie Mystique"
        cost = {Resource.CALM: 4, Resource.LIFE: 4}
        super().__init__(name, cost)


class SacredGrove(PlaceOfPower):
    def __init__(self):
        name = "Bosquet Sacré"
        cost = {Resource.CALM: 4, Resource.LIFE: 8}
        super().__init__(name, cost)


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
        return self.resources_on.resources[Resource.GOLD]


class DeathCatacomb(PlaceOfPower):
    def __init__(self):
        name = "Catacombes de la mort"
        cost = {Resource.DEATH: 9}
        super().__init__(name, cost)


class BloodyIsland(PlaceOfPower):
    def __init__(self):
        name = "Ile Sanguinaire"
        cost = {Resource.PEARL: 1, Resource.ELAN: 4, Resource.DEATH: 4}
        super().__init__(name, cost)


class PearlCradle(PlaceOfPower):
    def __init__(self):
        name = "Berceau de Perles"
        cost = {Resource.CALM: 6, Resource.GOLD: 3}
        super().__init__(name, cost)
    
    def collect_base(self, state, player):
        player.resources.add(Resource.PEARL, 1)
    
    def get_abilities(self):
        return super().get_abilities()


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


ALL_PLACES_OF_POWER = [MysticalMenagerie(),
                       SacredGrove(),
                       DragonsLair(),
                       DeathCatacomb(),
                       BloodyIsland(),
                       WizardBestiary()
                       ]