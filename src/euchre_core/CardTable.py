"""
compare.py

Provides logic for comparing Euchre cards based on trump and lead suit.
A central `lookup_table` is used to assign a rank to each card depending
on the context (trump suit and lead suit). Includes helper functions:

- `compare`: Returns a numerical comparison of two cards.
- `best_card`: Returns the stronger of two cards.
- `worst_card`: Returns the weaker of two cards.

Useful for determining trick winners and AI decisions.
"""

from typing import Optional

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
            lead (str, optional): The leading suit. Defaults to None.

        Returns:
            int: A positive number if left is greater than right,
                a negative number if right is greater than left,
                and 0 if they are equal.
        """

        lhs = self.dictionary[left]
        rhs = self.dictionary[right]
        return lhs - rhs


    def best_card(self, left: str, right: str) -> str:
        """
        Determine the best card between two cards.

        Args:
            left: The first card object.
            right: The second card object.
            lead (str, optional): The leading suit. Defaults to None.

        Returns:
            The better of the two cards based on the lookup table.
            When tied the left card is considered better.
        """
        compare = compare(left, right, trump, lead)
        if compare > 0:
            return left
        if compare < 0:
            return right
        return left


    def worst_card(self, left: str, right: str) -> int:
        """
        Determine the worst card between two cards.

        Args:
            left: The first card object.
            right: The second card object.
            lead (str, optional): The leading suit. Defaults to None.

        Returns:
            The worse of the two cards based on the lookup table.
            When tied the right card is considered worse.
        """
        compare = compare(left, right, trump, lead)
        if compare > 0:
            return right
        if compare < 0:
            return left
        return right

    def best_of(self, collection):
        if len(collection) == 0: 
            raise EuchreError("Can not get best card of empty set.")

        best = collection[0]
        for card in collection[1:]:
            best = self.best_card(best, card)

    def best(self, collection):
        if len(collection) == 0: 
            raise EuchreError("Can not get worst card of empty set.")

        worst = collection[0]
        for card in collection[1:]:
            best = self.worst_card(best, card)

    def observation(self):
        sb = ""
        for k, v in sorted(self.dictionary.items(), key=lambda x: x[1]):
            sb = sb + f"{k}: {v}\n"
        return sb
