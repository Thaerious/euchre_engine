# tests/test_deck.py
import pytest
import random
from euchre_core.Deck import Deck, SUITS, RANKS

def test_deck_initialization():
    d = Deck()
    # 24 unique cards
    assert len(d.cards) == 24
    assert sorted(d.cards) == sorted(r + s for s in SUITS for r in RANKS)
    # Order by suit grouping
    assert d.cards[:6] == [r + "♣" for r in RANKS]


def test_shuffle_changes_order_but_same_cards():
    rng = random.Random(123)
    d1 = Deck()
    d2 = Deck()
    d1.shuffle(rng)
    assert set(d1.cards) == set(d2.cards) # Test contents    
    assert d1.cards != d2.cards # Very unlikely to still match in order


def test_deal_returns_four_hands_and_upcard():
    rng = random.Random(0)
    d = Deck()
    d.shuffle(rng)
    hands, up = d.deal()

    # Each hand has 5 cards
    for h in hands:
        assert len(h) == 5

    # 3 cards remain
    assert len(d.cards) == 3

    # All cards unique across hands and up
    all_dealt = set(sum(hands, []) + [up]) # keeps unique only
    assert len(all_dealt) == 21

    # All valid cards
    assert all(c[-1] in SUITS and c[:-1] in RANKS for c in all_dealt)


def test_deal_reduces_deck_in_place():
    d = Deck()
    before = d.cards.copy()
    _ = d.deal()
    assert len(d.cards) == len(before) - 21
    
    # No overlap between remaining and dealt
    remaining = set(d.cards)
    dealt = set(before) - remaining
    assert remaining.isdisjoint(dealt)


def test_multiple_deals_exhaust_deck():
    d = Deck()
    d.deal()
    with pytest.raises(IndexError):
        d.deal()  # Not enough cards left
