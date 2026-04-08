from game.engine import Engine
from game.ai_player import AIPlayer
from utils.logger import Logger

from cards.artifacts import ALL_ARTIFACTS
from cards.mages import ALL_MAGES
from cards.objects import ALL_OBJECTS
from cards.place_of_power import ALL_PLACES_OF_POWER
from cards.monuments import ALL_MONUMENTS
from cards.scrolls import ALL_SCROLLS

if __name__ == "__main__":
    players = [AIPlayer("IA-Zib"), AIPlayer("IA-Kanss")]

    logger = Logger(level=3, silent=False)

    engine = Engine(
        players=players,
        mages=ALL_MAGES,
        artifacts=ALL_ARTIFACTS,
        monuments=ALL_MONUMENTS,
        places_of_power=ALL_PLACES_OF_POWER,
        objects=ALL_OBJECTS,
        scrolls=ALL_SCROLLS,
        logger=logger
    )

    engine.run()

    logger.save("logs/partie_ai", fmt="text")
    print(f"Partie terminée. Logs sauvegardés dans logs/partie_ai.log") #et logs/partie_ai.json")
