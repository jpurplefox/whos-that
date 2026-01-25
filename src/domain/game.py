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
    max_attempts: int = 4
    hints: list[Hint] = field(default_factory=list)
    attempts: list[Pokemon] = field(default_factory=list)

    def add_hint(self, stat: Stat) -> Hint:
        value = self.pokemon.get_stat(stat)
        hint = Hint(stat=stat, value=value)
        self.hints.append(hint)
        return hint

    def guess(self, pokemon: Pokemon) -> bool:
        if len(self.attempts) >= self.max_attempts:
            raise ValueError("No attempts remaining")
        self.attempts.append(pokemon)
        return pokemon.id == self.pokemon.id
