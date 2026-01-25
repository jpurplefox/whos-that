from dataclasses import dataclass, field

from domain.pokemon import Pokemon
from domain.stat import Stat


@dataclass
class Hint:
    stat: Stat
    value: int


@dataclass
class Game:
    pokemon: Pokemon
    hints: list[Hint] = field(default_factory=list)

    def add_hint(self, stat: Stat) -> Hint:
        value = self.pokemon.get_stat(stat)
        hint = Hint(stat=stat, value=value)
        self.hints.append(hint)
        return hint
