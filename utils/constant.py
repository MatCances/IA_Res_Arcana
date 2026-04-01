from enum import Enum

class Resource(Enum):
    LIFE = "life"
    DEATH = "death"
    GOLD = "gold"
    CALM = "calm"
    ELAN = "elan"
    PEARL = "pearl"
    ANY = "any"  # ressource fictive : n'importe quelle ressource

    @classmethod
    def real(cls):
        """Retourne toutes les ressources réelles (sans ANY)."""
        return [r for r in cls if r != cls.ANY]


class GameEvent(Enum):
    BUY_MONUMENT = "buy_monument"
    BUY_PLACE_OF_POWER = "buy_place_of_power"
    PLAY_ARTIFACT = "play_artifact"
    DISCARD_CARD = "discard_card"
    DESTROY_ARTIFACT = "destroy artifact"
    ATTACK = "attack"
    GET_GOLD = "get gold"
    VICTORY_CHECK = "victory_check"


class CardType(Enum):
    NONE = "none"
    DRAGON = "dragon"
    CREATURE = "creature"
    DEMON = "demon"
    ILLUSIONIST = "illusionist"