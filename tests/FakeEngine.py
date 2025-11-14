class FakeEngine:
    """
    A fake EuchreEngine used only for testing the Game FSM.
    Every method simply records that it was called.
    Return values can be set manually.
    """

    def __init__(self):
        # minimal engine state Game expects
        self.seat = 0
        self.dealer = 0
        self._tricks_taken = [0, 0]

        # return values you control in tests
        self._is_trick_finished = False
        self._is_hand_finished = False
        self._is_game_over = False
        self._trick_winner = 0

        # record which actions were called
        self.calls = []

    # --- Helpers for tests ---
    def reset_calls(self):
        self.calls.clear()

    # --- Engine methods Game interacts with ---

    def start_hand(self):
        self.calls.append(("start_hand",))

    def next_player(self):
        self.calls.append(("next_player",))
        self.seat = (self.seat + 1) % 4

    def order_up(self):
        self.calls.append(("order_up",))

    def go_alone(self):
        self.calls.append(("go_alone",))

    def pick_up(self, card):
        self.calls.append(("pick_up", card))

    def turn_down_card(self):
        self.calls.append(("turn_down_card",))

    def play_card(self, card):
        self.calls.append(("play_card", card))

    def add_trick_taken(self, team):
        self.calls.append(("add_trick_taken", team))
        self._tricks_taken[team] += 1

    def set_order(self, start_at):
        self.calls.append(("set_order", start_at))
        self.seat = start_at

    def score_hand(self):
        self.calls.append(("score_hand",))

    def inc_dealer(self):
        self.calls.append(("inc_dealer",))
        self.dealer = (self.dealer + 1) % 4

    # --- Engine status checks used by Game state transitions ---

    def is_trick_finished(self):
        return self._is_trick_finished

    def is_hand_finished(self):
        return self._is_hand_finished

    def is_game_over(self):
        return self._is_game_over

    def trick_winner(self):
        return self._trick_winner

    # Game.observation() needs this
    def observation(self):
        return {
            "seat": self.seat,
            "dealer": self.dealer,
            "taken": self._tricks_taken,
        }
