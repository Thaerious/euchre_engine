# tests/test_cardtable.py
import pytest
from euchre_core.CardTable import CardTable, SUITS, RANKS, OPPOSITE

def test_lookup_basics_trump_hearts_lead_clubs():
    table = CardTable(trump="♥", lead="♣")

    # Right/Left bowers have top values
    assert table.dictionary["J♥"] == 19
    assert table.dictionary["J♦"] == 18

    # Trump (non-bower) A is 17 (5 + 12)
    assert table.dictionary["A♥"] == 17

    # Lead bonus applies when lead != trump
    assert table.dictionary["Q♣"] == 3 + 6  # 9, beats many off-suit non-lead

    # Off-suit A without lead bonus
    assert table.dictionary["A♠"] == 5

def test_compare_order_examples():
    t = CardTable(trump="♥", lead="♣")
    # Right bower > left bower > A of trump
    assert t.compare("J♥", "J♦") > 0
    assert t.compare("J♦", "A♥") > 0

    # Any trump 9 beats any non-lead, non-trump Ace
    assert t.compare("9♥", "A♠") > 0

    # Lead bonus (lead=♣, not trump): Q♣ beats A♦
    assert t.compare("Q♣", "A♦") > 0

def test_lead_equals_trump_no_extra_bonus():
    # When lead==trump, only trump bonus should apply (no +6)
    t = CardTable(trump="♠", lead="♠")
    # A♠ should be 17, not 23
    assert t.dictionary["A♠"] == 5 + 12

def test_best_of_and_worst_of_and_errors():
    t = CardTable(trump="♣", lead="♥")
    cards = ["9♦", "A♣", "J♠", "K♥", "J♣"]  # includes right bower (J♣)
    assert t.best_of(cards) == "J♣"
    assert t.worst_of(cards) in cards  # specific worst depends on table; just ensure it returns a member

    with pytest.raises(ValueError):
        t.best_of([])
    with pytest.raises(ValueError):
        t.worst_of([])

def test_observation_sorted_and_has_24_lines():
    t = CardTable(trump="♥", lead="♣")
    obs = t.observation().strip().splitlines()
    assert len(obs) == 24
    # First line should be a lowest-ranked off-suit 9 (value 0)
    first_val = int(obs[0].split(": ")[1])
    last_val = int(obs[-1].split(": ")[1])
    assert first_val == 0
    assert last_val == 19
