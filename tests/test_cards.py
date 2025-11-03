# tests/test_cards.py
import pytest
from euchre_core.cards import card_suit, card_rank, same_color, is_left_bower, effective_suit

SUITS = ["♣", "♦", "♥", "♠"]
REDS  = {"♦", "♥"}
BLACKS = {"♣", "♠"}
RANKS = ["9", "10", "J", "Q", "K", "A"]

@pytest.mark.parametrize("card, exp_rank, exp_suit", [
    ("9♣",  "9",  "♣"),
    ("10♦", "10", "♦"),
    ("J♥",  "J",  "♥"),
    ("J♦",  "J",  "♦"),
    ("A♠",  "A",  "♠"),
])
def test_card_rank_and_suit(card, exp_rank, exp_suit):
    assert card_rank(card) == exp_rank
    assert card_suit(card) == exp_suit


@pytest.mark.parametrize("s1, s2, expect", [
    ("♦","♥", True),
    ("♥","♦", True),
    ("♣","♠", True),
    ("♠","♣", True),
    ("♦","♣", False),
    ("♥","♠", False),
    ("♣","♦", False),
    ("♠","♥", False),
])
def test_same_color(s1, s2, expect):
    assert same_color(s1, s2) is expect


@pytest.mark.parametrize("trump, left, right, others", [
    ("♥", "J♦", "J♥", ["J♣", "J♠"]),
    ("♦", "J♥", "J♦", ["J♣", "J♠"]),
    ("♠", "J♣", "J♠", ["J♦", "J♥"]),
    ("♣", "J♠", "J♣", ["J♦", "J♥"]),
])
def test_is_left_bower(trump, left, right, others):
    # Left bower detected
    assert is_left_bower(left, trump) is True
    # Right bower is NOT left bower
    assert is_left_bower(right, trump) is False
    # Other jacks are not left bowers
    for o in others:
        assert is_left_bower(o, trump) is False


@pytest.mark.parametrize("trump,card,expected", [
    # When trump is None, effective suit is the printed suit
    (None, "J♦", "♦"),
    (None, "10♣", "♣"),

    # Left bower adopts trump suit
    ("♥", "J♦", "♥"),
    ("♦", "J♥", "♦"),
    ("♠", "J♣", "♠"),
    ("♣", "J♠", "♣"),

    # Right bower stays trump (already the suit)
    ("♥", "J♥", "♥"),
    ("♣", "J♣", "♣"),

    # Non-bower cards keep their printed suit
    ("♥", "A♦", "♦"),
    ("♣", "10♠", "♠"),
    ("♦", "Q♦", "♦"),
    ("♠", "9♥", "♥"),
])
def test_effective_suit(trump, card, expected):
    assert effective_suit(card, trump) == expected


@pytest.mark.parametrize("trump", SUITS)
def test_effective_suit_only_left_bower_changes(trump):
    # All non-Jack cards should not change suit
    for s in SUITS:
        for r in ["9", "10", "Q", "K", "A"]:
            c = f"{r}{s}"
            assert effective_suit(c, trump) == s

    # Only the same-color Jack (not trump) changes
    if trump in REDS:
        same_color_other = (REDS - {trump}).pop()
    else:
        same_color_other = (BLACKS - {trump}).pop()
    left = f"J{same_color_other}"
    right = f"J{trump}"
    assert effective_suit(left, trump) == trump
    assert effective_suit(right, trump) == trump  # unchanged, already trump
