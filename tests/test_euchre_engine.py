"""
tests/test_euchre_engine.py
"""

import pytest
from euchre_core import EuchreEngine, EuchreError, card_suit, team_of, partner_of


@pytest.fixture
def engine():
    # fixed seed so Deck.shuffle is deterministic if we ever want to assert
    # specific cards later; for now we just assert invariants
    return EuchreEngine(seed=123)


@pytest.fixture
def stochastic_engine():
    engine = EuchreEngine(seed=123)

    # overwrite the dealt (empty) hands with legal Euchre cards
    engine._hands[0] = ["9♣", "J♦", "A♠", "Q♣", "K♥"]
    engine._hands[1] = ["10♠", "9♦", "K♣", "J♠", "Q♥"]
    engine._hands[2] = ["A♦", "10♥", "9♠", "K♦", "Q♠"]
    engine._hands[3] = ["A♥", "J♣", "10♣", "K♠", "Q♦"]

    # give an upcard so the engine is in a valid start-hand state
    engine._upcard = "A♣"

    return engine


@pytest.mark.init
def test_engine_initial_state(engine):
    assert engine.dealer == 0
    assert engine.tricks_played == 0
    assert not engine.is_game_over()


@pytest.mark.start_hand
def test_start_hand_initializes_core_state(engine):
    engine.start_hand()

    # 4 hands of 5 cards each
    assert len(engine._hands) == 4
    assert all(len(h) == 5 for h in engine._hands)

    # one upcard, no downcard yet, no discard
    assert engine._upcard is not None
    assert engine._downcard is None
    assert engine._discard is None

    # 5 empty tricks
    assert len(engine._tricks) == 5
    assert all(trick == [] for trick in engine._tricks)

    # trump not chosen, no maker yet
    assert engine._trump is None
    assert engine._maker is None

    # trick counters and points reset
    assert engine._tricks_taken == [0, 0]
    assert engine._points == [0, 0]

    # seat is left of the dealer, and player_order starts at that seat
    expected_first = (engine.dealer + 1) % 4
    assert engine.first_seat == expected_first
    assert engine.seat == expected_first
    assert engine.player_order == [
        expected_first,
        (expected_first + 1) % 4,
        (expected_first + 2) % 4,
        (expected_first + 3) % 4,
    ]

    # sanity: all known visible cards are unique (no dupes between hands+upcard)
    all_cards = [c for hand in engine._hands for c in hand] + [engine._upcard]
    assert len(set(all_cards)) == len(all_cards)


@pytest.mark.set_order
@pytest.mark.parametrize("start_at, order", [
    (-1, [3, 0, 1, 2]),
    (0, [0, 1, 2, 3]),
    (1, [1, 2, 3, 0]),
    (2, [2, 3, 0, 1]),
    (3, [3, 0, 1, 2]),
    (4, [0, 1, 2, 3])
])
def test_set_order_rotates_players(engine, start_at, order):
    engine.set_order(start_at)
    assert engine.player_order == order
    assert engine.seat == start_at % 4


@pytest.mark.inc_dealer
def test_inc_dealer_rotates_dealer(engine):
    assert engine.dealer == 0
    engine.inc_dealer()
    assert engine.dealer == 1
    engine.inc_dealer()
    assert engine.dealer == 2
    engine.inc_dealer()
    assert engine.dealer == 3
    engine.inc_dealer()
    assert engine.dealer == 0  # wraps


@pytest.mark.turn_down_card
def test_turn_down_card_moves_upcard(engine):
    engine.start_hand()
    old_upcard = engine._upcard

    engine.turn_down_card()

    assert engine.downcard == old_upcard
    assert engine.upcard is None


@pytest.mark.order_up
def test_order_up_sets_trump_and_maker(engine):
    engine.start_hand()
    seat_before = engine.seat
    up_suit = card_suit(engine._upcard)

    engine.order_up()

    assert engine.trump == up_suit
    assert engine.maker == seat_before  # maker is whoever ordered up


@pytest.mark.trump
def test_trump_cannot_match_downcard_suit(engine):
    engine.start_hand()

    # simulate that the upcard has been turned down
    engine.turn_down_card()              # now _downcard == old upcard
    down_suit = card_suit(engine._downcard)

    with pytest.raises(EuchreError):
        engine.trump = down_suit


@pytest.mark.team_of
def test_team_of_mapping():
    # even players -> team 0, odd -> team 1
    assert team_of(0) == 0
    assert team_of(1) == 1
    assert team_of(2) == 0
    assert team_of(3) == 1


@pytest.mark.pick_up
def test_pick_up_replaces_card_with_upcard(engine):
    engine.start_hand()
    dealer = engine.dealer
    dealers_hand = engine._hands[dealer]
    original_len = len(dealers_hand)
    old_upcard = engine.upcard

    card_to_discard = dealers_hand[0]
    engine.pick_up(card_to_discard)

    assert engine.discard == card_to_discard
    assert len(engine._hands[dealer]) == original_len
    assert old_upcard in engine._hands[dealer]
    assert card_to_discard not in engine._hands[dealer]


@pytest.mark.go_alone
def test_go_alone_removes_partner_from_order(engine):
    engine.start_hand()
    seat = engine.seat  # current maker
    partner = partner_of(seat)

    assert partner in engine.player_order

    engine.go_alone()

    assert engine.is_alone(seat)
    assert partner not in engine.player_order
    # still 3 players in order
    assert len(engine.player_order) == 3


@pytest.mark.trump
def test_set_trump_sets_maker_and_trump(engine):
    engine.start_hand()
    engine.trump = "♠"
    seat = engine.seat

    assert engine.maker == seat
    assert engine.trump == "♠"


@pytest.mark.go_alone
def test_go_alone_team_is_alone(engine):
    engine.start_hand()
    team = team_of(engine.seat)
    engine.go_alone()

    assert engine.is_team_alone(team)
    assert not engine.is_team_alone((team + 1) % 2)


@pytest.mark.next_player
def test_next_player_increments_seat_new_game(engine):
    engine.start_hand()

    assert engine.seat == 1
    engine.next_player()
    assert engine.seat == 2
    engine.next_player()
    assert engine.seat == 3
    engine.next_player()
    assert engine.seat == 0
    engine.next_player()
    assert engine.seat == 1


@pytest.mark.next_player
def test_next_player_wraps_around(engine):
    engine.start_hand()

    # force seat to last position
    engine.seat = 3
    engine.next_player()

    assert engine.seat == 0


@pytest.mark.next_player
@pytest.mark.parametrize("start, expected", [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
])
def test_next_player_parametric(engine, start, expected):
    engine.start_hand()
    engine.seat = start
    engine.next_player()
    assert engine.seat == expected


@pytest.mark.get_hand
def test_get_hand(engine):
    hand = engine.get_hand(0)
    assert hand == []

    engine.start_hand()
    hand = engine.get_hand(0)
    assert len(hand) == 5


@pytest.mark.play_card
def test_play_card_legal_play_removes_from_hand_and_adds_to_trick(engine):
    engine.start_hand()

    seat = engine.seat
    hand = engine.get_hand(seat)
    assert hand == ['J♦', 'Q♣', 'A♣', 'A♦', '10♦']  # from seed 123

    # current_trick should be empty at start of hand
    assert engine.current_trick == []
    engine.play_card('J♦')

    # card removed from player’s hand
    hand = engine.get_hand(seat)
    assert len(hand) == 4
    assert 'J♦' not in hand

    # card added to current_trick with (seat, card) tuple
    assert len(engine.current_trick) == 1
    assert engine.current_trick[0] == (seat, 'J♦')

    # play a second card
    engine.play_card('A♦')

    # card removed from player’s hand
    hand = engine.get_hand(seat)
    assert len(hand) == 3
    assert 'A♦' not in hand

    # card added to current_trick with (seat, card) tuple
    assert len(engine.current_trick) == 2
    assert engine.current_trick[1] == (seat, 'A♦')


@pytest.mark.play_card
def test_play_card_raises_if_card_not_in_hand(engine):
    engine.start_hand()

    seat = engine.seat
    # pick a card from a different player's hand so it's definitely illegal
    other_player = (seat + 1) % 4
    illegal_card = engine._hands[other_player][0]

    # sanity: illegal_card is not in current player's hand
    assert illegal_card not in engine._hands[seat]

    with pytest.raises(EuchreError):
        engine.play_card(illegal_card)


@pytest.mark.is_trick_finished
def test_is_trick_finished_basic(engine):
    engine.start_hand()

    # At start: trick empty → not finished
    assert not engine.is_trick_finished()

    # play 1 card → not finished
    card = engine.playable_cards()[0]
    engine.play_card(card)
    assert not engine.is_trick_finished()

    # play 2 cards → not finished
    card = engine.playable_cards()[0]
    engine.play_card(card)
    assert not engine.is_trick_finished()

    # play 3 cards → not finished
    card = engine.playable_cards()[0]
    engine.play_card(card)
    assert not engine.is_trick_finished()

    # play 4th card → finished
    card = engine.playable_cards()[0]
    engine.play_card(card)
    assert engine.is_trick_finished()


@pytest.mark.score_hand
def test_score_hand_defenders_euchre_not_alone(engine):
    # maker is player 0 → makers team = 0, defenders team = 1
    engine._maker = 0
    engine._tricks_taken = [2, 3]   # defenders > makers
    engine._alone = []              # nobody alone
    engine._points = [0, 0]

    engine.score_hand()

    assert engine._points == [0, 2]  # defenders get 2 points


@pytest.mark.score_hand
def test_score_hand_defenders_euchre_alone(engine):
    engine._maker = 0
    engine._tricks_taken = [2, 3]   # defenders > makers
    engine._alone = [1]             # a defender (team 1) went alone
    engine._points = [0, 0]

    engine.score_hand()

    assert engine._points == [0, 4]  # defenders get 4 points for lone euchre


@pytest.mark.score_hand
def test_score_hand_makers_win_normal(engine):
    engine._maker = 0
    engine._tricks_taken = [3, 2]   # makers > defenders, makers < 5
    engine._alone = []
    engine._points = [0, 0]

    engine.score_hand()

    assert engine._points == [1, 0]  # makers get 1 point


@pytest.mark.score_hand
def test_score_hand_makers_sweep_not_alone(engine):
    engine._maker = 0
    engine._tricks_taken = [5, 0]   # makers took all 5
    engine._alone = []
    engine._points = [0, 0]

    engine.score_hand()

    assert engine._points == [2, 0]  # makers get 2 points for a sweep


@pytest.mark.score_hand
def test_score_hand_makers_sweep_alone(engine):
    engine._maker = 0
    engine._tricks_taken = [5, 0]
    engine._alone = [0]             # maker (team 0) went alone
    engine._points = [0, 0]

    engine.score_hand()

    assert engine._points == [4, 0]  # makers get 4 points for lone sweep


@pytest.mark.score_hand
def test_score_hand_both_teams_alone_defenders_euchre(engine):
    engine._maker = 0
    engine._tricks_taken = [2, 3]     # defenders win
    engine._alone = [0, 1]            # maker (team 0) AND defender (team 1) both flagged alone
    engine._points = [0, 0]

    engine.score_hand()

    # defenders are alone → defenders get 4
    assert engine._points == [0, 4]


@pytest.mark.score_hand
def test_score_hand_both_teams_alone_maker_wins(engine):
    engine._maker = 0
    engine._tricks_taken = [3, 2]     # makers win (but not sweep)
    engine._alone = [0, 1]            # both teams have someone alone
    engine._points = [0, 0]

    engine.score_hand()

    # makers are alone → makers get 1 (lone doesn't matter unless sweep)
    assert engine._points == [1, 0]


@pytest.mark.score_hand
def test_score_hand_both_teams_alone_maker_sweep(engine):
    engine._maker = 0
    engine._tricks_taken = [5, 0]     # makers sweep
    engine._alone = [0, 1]            # both teams marked alone
    engine._points = [0, 0]

    engine.score_hand()

    # makers alone → lone sweep = 4 points
    assert engine._points == [4, 0]


@pytest.mark.add_trick_taken
def test_add_trick_taken_increments_team_count(engine):
    # start from clean state
    assert engine._tricks_taken == [0, 0]
    assert engine.tricks_played == 0

    engine.add_trick_taken(0)
    assert engine._tricks_taken == [1, 0]
    assert engine.tricks_played == 1

    engine.add_trick_taken(1)
    assert engine._tricks_taken == [1, 1]
    assert engine.tricks_played == 2

    engine.add_trick_taken(0)
    assert engine._tricks_taken == [2, 1]
    assert engine.tricks_played == 3


@pytest.mark.is_hand_finished
def test_is_hand_finished_depends_on_total_tricks(engine):
    # simulate tricks being taken via add_trick_taken
    for _ in range(4):
        engine.add_trick_taken(0)  # same team, doesn't matter for finish

    assert engine.tricks_played == 4
    assert not engine.is_hand_finished()

    # 5th trick → hand finished
    engine.add_trick_taken(1)
    assert engine.tricks_played == 5
    assert engine.is_hand_finished()

    # extra tricks (defensive: shouldn’t happen in real play, but code allows)
    engine.add_trick_taken(0)
    assert engine.tricks_played == 6
    assert engine.is_hand_finished()  # still finished once >= 5


@pytest.mark.trick_winner
def test_trick_winner_regular_follow_suit(engine):
    engine._trump = "♥"                # trump irrelevant here
    engine._tricks = [[] for _ in range(5)]
    engine._tricks[0] = [
        (0, "9♣"),   # lead
        (1, "K♣"),
        (2, "J♦"),
        (3, "A♣"),
    ]

    assert engine.trick_winner() == 3
