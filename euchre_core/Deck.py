import random
from typing import List, Tuple
from .cards import IDX2CARD

class Deck:
    def __init__(self):
        self.cards = IDX2CARD.copy()

    def shuffle(self, rng: random.Random) -> None:
        rng.shuffle(self.cards)

    def deal(self) -> Tuple[List[str], List[str], List[str], List[str], str]:
        hands = [[], [], [], []]
        
        for _ in range(5):
            for p in range(4):
                hands[p].append(self.cards.pop())

        up = self.cards.pop()
        return hands[0], hands[1], hands[2], hands[3], up