from typing import Protocol


class RandomGenerator(Protocol):
    def randint(self, min_value: int, max_value: int) -> int: ...
