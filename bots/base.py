
from typing import Protocol
from euchre_core import Observation, ActionMask, ActionKind

class Bot(Protocol):
    def act(self, obs: Observation, mask: ActionMask, kind: ActionKind) -> int: ...
