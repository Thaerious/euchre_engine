
from typing import Dict, List

SUITS = ["♣", "♦", "♥", "♠"]
RANKS = ["9", "10", "J", "Q", "K", "A"]

IDX2CARD: List[str] = [r + s for s in SUITS for r in RANKS]
CARD2IDX: Dict[str, int] = {c:i for i,c in enumerate(IDX2CARD)}

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

def trump_order(trump: str) -> Dict[str, int]:
    order: Dict[str, int] = {}
    base = {r:i for i,r in enumerate(RANKS)}
    for c in IDX2CARD:
        r = card_rank(c); s = card_suit(c)
        strength = base[r]
        if s == trump:
            strength += 10
        if r == "J":
            if s == trump:
                strength = 17
            elif same_color(s, trump):
                strength = 16
        order[c] = strength
    return order
