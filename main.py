from game.engine import Engine
from game.player import Player
from cards.artifacts import ALL_ARTIFACTS
from cards.mages import ALL_MAGES
from cards.objects import ALL_OBJECTS
from cards.place_of_power import ALL_PLACES_OF_POWER
from cards.monuments import ALL_MONUMENTS
from cards.scrolls import ALL_SCROLLS

if __name__ == "__main__":
    players = [Player("Kanss"), Player("Zib")]

    engine = Engine(
        players=players,
        mages=ALL_MAGES,
        artifacts=ALL_ARTIFACTS,
        monuments=ALL_MONUMENTS,
        places_of_power=ALL_PLACES_OF_POWER,
        objects=ALL_OBJECTS,
        scrolls=ALL_SCROLLS
    )

    engine.run()