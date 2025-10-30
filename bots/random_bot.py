
import random
from euchre_core import Observation, ActionMask, ActionKind

class RandomBot:
    def __init__(self, seed: int|None=None):
        self.rng = random.Random(seed)
    def act(self, obs: Observation, mask: ActionMask, kind: ActionKind) -> int:
        legal = [i for i,v in enumerate(mask) if v==1]
        return self.rng.choice(legal) if legal else 0
