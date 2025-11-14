"""
Game.py
maintains the finite state machine for a euchre game
"""

# pylint ignore attribute and public method counts
# pylint: disable=R0902, R0904

from .EuchreEngine import EuchreEngine, team_of
from .EuchreError import EuchreError
from .cards import card_suit
from collections.abc import Callable
from typing import Any

class Game():
    """
    Manages the overall flow and state of a Euchre game.
    """

    def __init__(self, engine: EuchreEngine, names: list[str]):
        """
        Initialize the Game object with player names.

        Args:
            names (list of str): List of player names.
        """
        self._engine = engine
        self._names = names.copy()
        self._state: Callable[[str, Any], None] = self.state_0
        self.last_action: str | None = None
        self.last_data: str | None = None
        self.do_shuffle = True

    @property
    def state(self) -> int:
        """
        Get the current state as an integer.

        Returns:
            int: Current state number.
        """
        return int(self._state.__name__[6:])

    def observation(self):
        return {
            **self._engine.observation(),
            "state": self.state,
            "last_action": self.last_action,
            "last_data": self.last_data
        }

    def input(self, action: str, data: str | None = None,) -> None:
        """
        Process player input based on the current game state.

        Args:
            player (Optional[str]): Name of the player performing the action.
            action (str): Action to perform.
            data (Optional[Union[str, Card]], optional): Additional data for the action.

        Raises:
            ActionException: If the action or player is invalid.
        """
        prev_state = self.state

        self.last_action = action

        if action in ["play", "make"]:
            self.last_data = data
        else:
            self.last_data = None

        self._state(action, data)

    def state_0(self, action: str, __: Any) -> None:
        """
        Initial state where the game starts.

        Args:
            action (str): Expected action "start".
            __: Unused parameter.
        """
        self.allowed_actions(action, "start")
        self.enter_state_1()

    def enter_state_1(self) -> None:
        """
        Transition to state 1: Shuffle and deal cards.
        """
        self._engine.start_hand()
        self._state = self.state_1

    def state_1(self, action: str, __: Any) -> None:
        """
        State 1: Players decide to pass, order up, or go alone.

        Args:
            action (str): Action to perform ("pass", "order", "alone").
            __: Unused parameter.
        """
        self.allowed_actions(action, "pass", "order", "alone")

        if action == "pass":
            self._engine.next_player()
            if self._engine.seat == self._engine.dealer:                
                self.enter_state_3()
        elif action == "order":  
            self._engine.order_up()
            self.enter_state_2()
        elif action == "alone":
            self._engine.order_up()
            self._engine.go_alone()
            self.enter_state_2()

    def enter_state_2(self) -> None:
        """
        Transition to state 2: Dealer's turn to decide.
        """
        self._engine.seat = self._engine.dealer
        self._state = self.state_2

    def state_2(self, action: str, card: str | None) -> None:
        """
        State 2: Dealer decides to pick up the card or pass.

        Args:
            action (str): Action to perform ("down", "up").
            card (Card): Card to swap if action is "up".
        """
        self.allowed_actions(action, "down", "up")
        self._engine.dealer_action = action

        if action == "up": 
            self._engine.pick_up(card)

        self._engine.seat = self._engine.dealer + 1
        self.enter_state_5()

    def enter_state_3(self):
        """
        Transition to state 3: Dealer turns down the up-card,
        and players begin selecting a trump suit.
        """
        self._engine.turn_down_card()
        self._state = self.state_3

    def state_3(self, action: str, suit: str | None) -> None:
        """
        State 3: Players decide to pass, make, or go alone for trump.

        Args:
            action (str): Action to perform ("pass", "make", "alone").
            suit (str): Trump suit if "make" or "alone".
        """
        self.allowed_actions(action, "pass", "make", "alone")

        if action == "pass":
            self._engine.next_player()
            if self._engine.seat == self._engine.dealer:                
                self.enter_state_4()
        elif action == "make":
            self._engine.trump = suit
            self._engine.seat = self._engine.dealer + 1
            self.enter_state_5()
        elif action == "alone":
            self._engine.go_alone()
            self._engine.trump == suit
            self._engine.seat = self._engine.dealer + 1
            self.enter_state_5()


    def enter_state_4(self) -> None:
        """
        Transition to state 4: Dealer decides to make trump or go alone.
        """
        self._state = self.state_4

    def state_4(self, action: str, suit: str | None) -> None:
        """
        State 4: Dealer decides to make trump or go alone.

        Args:
            action (str): Action to perform ("make", "alone").
            suit (str): Trump suit.
        """
        self.allowed_actions(action, "make", "alone")

        if action == "alone":
            self.players.go_alone()

        self._engine.trump = suit
        self._engine.seat = self._engine.dealer + 1
        self.enter_state_5()

    def enter_state_5(self) -> None:
        """
        Transition to state 5: Players play tricks.
        """
        self._state = self.state_5

    def state_5(self, action: str, card: str) -> None:
        """
        State 5: Players play cards and score tricks.

        Args:
            action (str): Expected action "play".
            card (Card): Card to play.
        """
        self.allowed_actions(action, "play")
        self._engine.play_card(card)               

        if not self._engine.is_trick_finished(): 
            self._engine.next_player()
        else:
            self.enter_state_6()

    def enter_state_6(self) -> None:
        """
        Transition to state 6: Score the current trick and
        determine whether to continue playing or move to scoring the hand.
        """
        trick_winner = self._engine.trick_winner()
        team = team_of(trick_winner)
        self._engine.add_trick_taken(team)
        self._engine.set_order(trick_winner)

        self._state = self.state_6

    def state_6(self, action: str, __: Any) -> None:
        """
        State 6: Transition to the next trick.

        Args:
            action (str): Expected action "continue".
            __: Unused parameter.
        """
        self.allowed_actions(action, "continue")

        if not self._engine.is_hand_finished():           
            self.enter_state_5()
        else:
            self._engine.score_hand()
            self._state = self.state_7

    def state_7(self, action: str, __: Any) -> None:
        """
        State 7: Transition to the next hand.

        Args:
            action (str): Expected action "continue".
            __: Unused parameter.
        """
        self.allowed_actions(action, "continue")

        if self._engine.is_game_over():
            self._state = self.state_8
        else:
            self._engine.inc_dealer()
            self.enter_state_1()

    def state_8(self, _: str, __: Any) -> None:
        """
        State 8: Game over, no transitions.
        """
        # pylint: disable=W0107
        pass

    def allowed_actions(self, action: str, *allowed_actions: str) -> None:
        """
        Validate if the given action is allowed in the current state.

        Args:
            action (str): Action to validate.
            allowed_actions (list of str): List of allowed actions.

        Raises:
            ActionException: If the action is not allowed.
        """

        for allowed in allowed_actions:
            if action.lower() == allowed.lower():
                return

        raise EuchreError("Unhandled Action " + str(action))

    def __json__(self):
        return super().__json__() | {
            "hash": self.hash,
            "state": self.state,
            "last_action": self.last_action,
        }

    def to_json(self, indent=2):
        """
        Serialize the Euchre game state to a JSON-formatted string.

        Args:
            indent (int, optional): Number of spaces to use for indentation in the output. Defaults to 2.

        Returns:
            str: A JSON-formatted string representation of the game state.
        """
        return json.dumps(self, indent=indent, default=custom_json_serializer)   

def int_or_none(source):
    """
    Convert a value to int if not None.

    Args:
        source (Any): The source value.

    Returns:
        Optional[int]: Integer value or None.
    """
    if source is None:
        return None
    return int(source)


def card_or_none(deck, source):
    """
    Convert a dictionary or string to a Card if not None.

    Args:
        deck (Deck): Reference to the current Deck object.
        source (dict or str): JSON representation of a card.

    Returns:
        Optional[Card]: Card object or None.
    """
    if source is None:
        return None
    return Card(deck, source)