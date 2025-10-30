
from euchre_core import Observation, ActionMask, ActionKind
from euchre_core.cards import effective_suit

class RuleBot:
    """Tiny heuristic bot:
    - Bid phase: pass.
    - Play phase: follow suit with weakest legal; otherwise play weakest legal.
    """
    def act(self, obs: Observation, mask: ActionMask, kind: ActionKind) -> int:
        if kind == "bid":
            return 0
        hand = obs["hand"]
        trump = obs["trump"]
        legal = [i for i,v in enumerate(mask) if v==1]
        if not obs["current_trick"]:
            return min(legal)
        led_card = obs["current_trick"][0][1]
        must = effective_suit(led_card, trump)
        follow = [i for i in legal if effective_suit(hand[i], trump)==must]
        pool = follow if follow else legal
        return min(pool)
