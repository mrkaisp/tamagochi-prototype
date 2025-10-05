from __future__ import annotations

import random
from typing import Optional


class RandomManager:
    """Centralized RNG with optional fixed seed for reproducibility."""

    _instance: Optional["RandomManager"] = None

    def __init__(self, seed: Optional[int] = None):
        self._seed = seed
        self._rng = random.Random(seed)

    @classmethod
    def get_instance(cls) -> "RandomManager":
        if cls._instance is None:
            cls._instance = RandomManager()
        return cls._instance

    def set_seed(self, seed: Optional[int]) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def get_seed(self) -> Optional[int]:
        return self._seed

    def random(self) -> float:
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq):
        return self._rng.choice(seq)


def get_rng() -> RandomManager:
    return RandomManager.get_instance()


