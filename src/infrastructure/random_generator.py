import random
from typing import Protocol


class RandomGenerator(Protocol):
    def randint(self, min_value: int, max_value: int) -> int:
        ...


class SystemRandomGenerator:
    def randint(self, min_value: int, max_value: int) -> int:
        return random.randint(min_value, max_value)
