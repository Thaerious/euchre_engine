"""
Cards.py
"""

from typing import Dict, List

def card_suit(card: str) -> str:
    return card[-1]

def card_rank(card: str) -> str:
    return card[:-1]

def same_color(s1: str, s2: str) -> bool:
    red = {"♦", "♥"}
    black = {"♣", "♠"}
    return (s1 in red and s2 in red) or (s1 in black and s2 in black)

def is_left_bower(card: str, trump: str) -> bool:
    return card_rank(card) == "J" and card_suit(card) != trump and same_color(card_suit(card), trump)

def effective_suit(card: str, trump: str|None) -> str:
    if trump is not None and is_left_bower(card, trump):
        return trump
    return card_suit(card)