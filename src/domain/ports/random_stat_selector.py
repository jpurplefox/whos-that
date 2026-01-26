from typing import Protocol

from domain.stat import Stat


class RandomStatSelector(Protocol):
    def select(self) -> Stat:
        ...
