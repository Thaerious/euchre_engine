
from __future__ import annotations
import random
from typing import List, Tuple, Dict, Optional, TypedDict, Literal
from .cards import SUITS, RANKS, IDX2CARD, effective_suit, card_suit, trump_order
from .Deck import Deck
from .EuchreError import EuchreError
from .compare_cards import best_card, compare_cards
import traceback

ActionKind = Literal["bid", "play"]

class EuchreEngine:
    """Pure game engine. No bot logic here."""
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.points = [0, 0]
        self.dealer = 0

    def start_hand(self):
        self.phase: Literal["bidding","playing"] = "bidding"
        deck = Deck()
        deck.shuffle(self.rng)
        h0, h1, h2, h3, self.upcard = deck.deal()

        self.alone = [] # list of players that have gone alone
        self.discard = None # card discarded by dealer
        self.hands = [h0,h1,h2,h3] # array of hands returned from deck shuffle
        self.tricks = [[] for _ in range(5)] # array of tricks
        self.trump: Optional[str] = None # current trump
        self.tricks_taken = [0,0] # count of tricks taken for each team
        self.seat = (self.dealer + 1) % 4 # the current player performing an action
        self.maker: Optional[int] = None # the player that made trump
        self.order = trump_order("♣") # dictionary of card -> value
        self.set_order(self.dealer + 1) # order of players performing actions

    def next_hand(self):
        self.dealer = (self.dealer + 1) % 4

    @property
    def tricks_played(self):
        return sum(self.tricks_taken)

    def leader(self): 
        self.player_order[0]

    def go_alone(self): 
        self.alone.push(self.seat)
        self.player_order.remove((self.seat + 2) % 4)

    def next_player(self):
        self.seat = (self.seat + 1) % 4

    def play_card(self, card):
        if not card in self.playable_cards():
            raise EuchreError(f"Card '{card}' is not a legal play.")

        hand = self.hands[self.seat]
        hand.remove(card)
        self.current_trick.append((self.seat, card))

    def score_hand(self):
        makers = team_of(self.maker)
        defenders = (makers + 1) % 2

        if self.tricks_taken[defenders] > self.tricks_taken[makers]:
            if self.is_team_alone(defenders): self.points[defenders] += 4
            else: self.points[defenders] += 2
        elif self.tricks_taken[makers] < 5:
            self.points[makers] += 1
        else:
            if self.is_team_alone(makers): self.points[makers] += 4
            else: self.points[makers] += 2

    def is_team_alone(self, team: int) -> bool:
        return team in self.alone or ((team + 2) % 4) in self.alone

    @property
    def current_trick(self):
        return self.tricks[self.tricks_played]

    def is_trick_finished(self) -> bool: 
        return len(self.current_trick) == len(self.player_order)

    def is_hand_finished(self) -> bool:
        return self.tricks_played >= 5

    def set_order(self, start_at):
        self.player_order = [(i + start_at) % 4 for i in range(0,4)]
        self.seat = self.player_order[0]

    def playable_cards(self):
        if self.tricks_played >= 5: return []

        hand = self.hands[self.seat]
        if len(self.current_trick) == 0: return hand
        lead_card = self.current_trick[0][1]
        playable = []

        for card in hand:
            if effective_suit(card, self.trump) == effective_suit(lead_card, self.trump):
                playable.append(card)

        if len(playable) > 0: return playable
        return hand

    def trick_winner(self):
        best_seat, best_card = self.current_trick[0]
        lead_suit = effective_suit(best_card, self.trump)

        for seat, card in self.current_trick[1:]:
            compare = compare_cards(best_card, card, self.trump, lead_suit)
            if compare < 0: best_seat, best_card = seat, card

        return best_seat

    def is_game_over(self):
        return self.points[0] >= 10 or self.points[1] >= 10

    def observation(self):
        return {
            "phase": self.phase,
            "seat": self.seat,
            "dealer": self.dealer,
            "maker": self.maker,
            "player_order": self.player_order,
            "hands": self.hands,
            "trump": self.trump,
            "upcard": self.upcard,
            "tricks": self.tricks,
            "taken": self.tricks_taken,
            "points": list(self.points),
        }
    
def team_of(player: int):
    return (player % 2)    
