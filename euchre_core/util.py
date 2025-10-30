
from typing import Iterable, List
def mask_from_indices(n:int, on: Iterable[int]) -> List[int]:
    m = [0]*n
    for i in on:
        if 0 <= i < n: m[i] = 1
    return m
