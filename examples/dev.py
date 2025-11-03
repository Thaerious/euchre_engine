from euchre_core import EuchreEngine, Game
from pprint import pprint

engine = EuchreEngine(42)
game = Game(engine, ["Adam", "Cain", "Eve", "Able"])

game.input("start", None)
game.input("pass")
game.input("pass")
game.input("pass")
game.input("pass")

game.input("pass")
game.input("pass")
game.input("pass")

pprint(game.observation())
game.input("make", "♣")

# game.input("order", None)
# game.input("up", "10♦")

# game.input("play", "A♥")
# game.input("play", "K♥")
# game.input("play", "10♥")
# game.input("play", "9♥")
# game.input("continue", None)

# game.input("play", "10♠")
# game.input("play", "9♣")
# game.input("play", "Q♠")
# game.input("play", "A♠")
# game.input("continue", None)

# game.input("play", "J♠")
# game.input("play", "10♣")
# game.input("play", "9♦")
# game.input("play", "K♠")
# game.input("continue", None)

# game.input("play", "J♣")
# game.input("play", "Q♣")
# game.input("play", "K♣")
# game.input("play", "J♥")
# game.input("continue", None)

# game.input("play", "A♦")
# game.input("play", "Q♦")
# game.input("play", "K♦")
# game.input("play", "J♦")
# game.input("continue", None)
# game.input("continue", None)

pprint(game.observation())
pprint(engine.playable_cards())