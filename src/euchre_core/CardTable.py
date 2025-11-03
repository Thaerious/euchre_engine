"""
CardTable.py

Provides logic for comparing Euchre cards based on trump and lead suit.
A central `lookup_table` is used to assign a rank to each card depending
on the context (trump suit and lead suit). Includes helper functions:

- `compare`: Returns a numerical comparison of two cards.
- `best_card`: Returns the stronger of two cards.
- `worst_card`: Returns the weaker of two cards.

Useful for determining trick winners and AI decisions.
"""

from typing import Optional, Iterable

OPPOSITE = {"♠":"♣", "♥":"♦", "♣":"♠", "♦":"♥"}
SUITS = ["♠", "♥", "♣", "♦"]
RANKS = ["9", "10", "J", "Q", "K", "A"]

class CardTable:
    def __init__(self, trump: str, lead: str):
        self.dictionary = {}

        for suit in SUITS:
            for rank in RANKS:
                value = RANKS.index(rank)
                if suit == trump: value = value + 12
                if lead != trump and suit == lead: value = value + 6

                self.dictionary[f"{rank}{suit}"] = value

        # Override right/left bower
        if trump is not None:
            self.dictionary[f"J{trump}"] = 19
            self.dictionary[f"J{OPPOSITE[trump]}"] = 18


    def compare(self, left: str, right: str) -> int:
        """
        Compare two cards based on their value in the lookup table.

        Args:
            left: The first card object.
            right: The second card object.

        Returns:
            int: A positive number if left is greater than right,
                a negative number if right is greater than left,
                and 0 if they are equal.
        """

        return self.dictionary[left] - self.dictionary[right]
   

    def best_of(self, collection: Iterable[str]):
        collection = list(collection)

        if not collection:
            raise ValueError("Collection cannot be empty")

        best = collection[0]
        for card in collection[1:]:
            best = best if self.compare(best, card) >= 0 else card

        return best


    def worst_of(self, collection: Iterable[str]):
        collection = list(collection)

        if not collection:
            raise ValueError("Collection cannot be empty")

        worst = collection[0]
        for card in collection[1:]:
            worst = card if self.compare(worst, card) >= 0 else worst

        return worst

    def observation(self):
        sb = ""
        for k, v in sorted(self.dictionary.items(), key=lambda x: x[1]):
            sb = sb + f"{k}: {v}\n"
        return sb
