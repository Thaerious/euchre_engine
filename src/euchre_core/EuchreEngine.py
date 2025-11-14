"""
EuchreEngine.py
"""

from __future__ import annotations
import random
from typing import List, Tuple, Dict, Optional, TypedDict, Literal
from .cards import effective_suit, card_suit
from .Deck import Deck
from .EuchreError import EuchreError
from .CardTable import CardTable
import traceback

class EuchreEngine:
    """Pure game engine. No bot logic here."""
    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)
        self._points = [0, 0]
        self._dealer = 0
        self._clear()

    def _clear(self):
        self._downcard = None
        self._alone = [] # list of players that have gone alone
        self._discard = None # card discarded by dealer
        self._hands = [[],[],[],[]] # array of hands returned from deck shuffle
        self._tricks = [[] for _ in range(5)] # array of tricks
        self._trump: Optional[str] = None # current trump
        self._tricks_taken = [0,0] # count of tricks taken for each team
        self._seat = (self._dealer + 1) % 4 # the current player performing an action
        self._maker: Optional[int] = None # the player that made trump
        self.set_order(self._dealer + 1) # order of players performing actions
        self.card_table = CardTable(None, None) # lookup table for card values        

    def start_hand(self):
        self._clear()        
        deck = Deck()
        deck.shuffle(self._rng)
        self._hands, self._upcard = deck.deal()


    @property
    def trump(self) -> Optional[str]: return self._trump

    @trump.setter
    def trump(self, suit):
        if self._downcard is not None and suit == card_suit(self._downcard):
            raise EuchreError(f"Can not declare same suit ({suit}) as downcard ({self._downcard}).")

        self._maker = self._seat
        self._trump = suit

    @property
    def maker(self) -> Optional[int]: return self._maker

    @property
    def downcard(self) -> Optional[str]: return self._downcard

    @property
    def upcard(self) -> Optional[str]: return self._upcard

    @property
    def discard(self) -> Optional[str]: return self._discard

    @property
    def seat(self) -> int: return self._seat

    @seat.setter
    def seat(self, value): self._seat = value % 4

    @property
    def dealer(self) -> int: return self._dealer

    @property
    def tricks_played(self): return sum(self._tricks_taken)

    @property
    def first_seat(self): return self.player_order[0]

    @property
    def current_trick(self): return self._tricks[self.tricks_played]

    def get_hand(self, index): 
        return self._hands[index % 4].copy()

    def is_team_alone(self, team: int) -> bool:
        return team in self._alone or partner_of(team) in self._alone

    def turn_down_card(self):
        self._downcard = self._upcard
        self._upcard = None

    def inc_dealer(self):
        self._dealer = (self._dealer + 1) % 4

    def order_up(self):
        self._trump = card_suit(self._upcard)
        self._maker = self._seat

    def pick_up(self, card):
        dealers_hand = self._hands[self.dealer]   
        dealers_hand.remove(card)  
        self._discard = card
        dealers_hand.append(self._upcard)     

    def is_alone(self, seat):
        return seat in self._alone

    def go_alone(self): 
        self._alone.append(self.seat)
        self.player_order.remove(partner_of(self.seat))

    def next_player(self):
        self._seat = (self._seat + 1) % 4

    def play_card(self, card):
        if len(self.current_trick) == 0:
            self.card_table = CardTable(self._trump, card_suit(card))

        if not card in self.playable_cards():
            raise EuchreError(f"Card '{card}' is not a legal play.")

        hand = self._hands[self._seat]
        hand.remove(card)
        self.current_trick.append((self._seat, card))

    def score_hand(self):
        makers = team_of(self._maker)
        defenders = (makers + 1) % 2

        if self._tricks_taken[defenders] > self._tricks_taken[makers]:
            if self.is_team_alone(defenders): self._points[defenders] += 4
            else: self._points[defenders] += 2
        elif self._tricks_taken[makers] < 5:
            self._points[makers] += 1
        else:
            if self.is_team_alone(makers): self._points[makers] += 4
            else: self._points[makers] += 2

    def add_trick_taken(self, team: int):
        self._tricks_taken[team] += 1

    def is_trick_finished(self) -> bool: 
        return len(self.current_trick) == len(self.player_order)

    def is_hand_finished(self) -> bool:
        return self.tricks_played >= 5

    def set_order(self, start_at):
        self.player_order = [(i + start_at) % 4 for i in range(0,4)]
        self._seat = self.first_seat

    def playable_cards(self):
        if self.tricks_played >= 5: return []

        hand = self._hands[self._seat]
        if len(self.current_trick) == 0: return hand
        lead_card = self.current_trick[0][1]
        playable = []

        for card in hand:
            if effective_suit(card, self._trump) == effective_suit(lead_card, self._trump):
                playable.append(card)

        if len(playable) > 0: return playable
        return hand

    def trick_winner(self):
        best_seat, best_card = self.current_trick[0]
        lead_suit = effective_suit(best_card, self._trump)

        for seat, card in self.current_trick[1:]:
            compare = self.card_table.compare(best_card, card)
            if compare < 0: best_seat, best_card = seat, card

        return best_seat

    def is_game_over(self):
        return self._points[0] >= 10 or self._points[1] >= 10

    def observation(self):
        return {
            "seat": self._seat,
            "dealer": self._dealer,
            "maker": self._maker,
            "player_order": self.player_order,
            "hands": self._hands,
            "trump": self._trump,
            "upcard": self._upcard,
            "downcard": self._downcard,
            "discard": self._discard,
            "tricks": self._tricks,
            "taken": self._tricks_taken,
            "points": list(self._points),
        }
    
def team_of(player: int):
    return (player % 2)    

def partner_of(player: int):
    return (player + 2) % 4