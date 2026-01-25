from dataclasses import dataclass

from domain.stat import Stat


@dataclass
class Pokemon:
    id: int
    name: str
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int

    def get_stat(self, stat: Stat) -> int:
        return getattr(self, stat.value)
