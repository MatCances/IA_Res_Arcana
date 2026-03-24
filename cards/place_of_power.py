from cards.base_card import Card
from utils.constant import Resource


class PlaceOfPower(Card):
    def __init__(self, name, cost):
        super().__init__(name, cost=cost)


class MysticalMenagerie(PlaceOfPower):
    def __init__(self):
        name = "Mystical Menagerie"
        cost = {Resource.CALM: 4, Resource.LIFE: 4}
        super().__init__(name, cost)


class SacredGrove(PlaceOfPower):
    def __init__(self):
        name = "Sacred Grove"
        cost = {Resource.CALM: 4, Resource.LIFE: 8}
        super().__init__(name, cost)


class DragonsLair(PlaceOfPower):
    def __init__(self):
        name = "Dragon's Lair"
        cost = {Resource.ELAN: 8, Resource.LIFE: 4}
        super().__init__(name, cost)


class DeathCatacomb(PlaceOfPower):
    def __init__(self):
        name = "Death catacomb"
        cost = {Resource.DEATH: 9}
        super().__init__(name, cost)


class BloodyIsland(PlaceOfPower):
    def __init__(self):
        name = "Bloody Island"
        cost = {Resource.PEARL: 1, Resource.ELAN: 4, Resource.DEATH: 4}
        super().__init__(name, cost)


ALL_PLACES_OF_POWER = [
    MysticalMenagerie(), SacredGrove(), DragonsLair(),
    DeathCatacomb(), BloodyIsland()
]