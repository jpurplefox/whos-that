from dataclasses import dataclass, field
from enum import Enum

from domain.pokemon import Pokemon
from domain.stat import Stat


class NoAttemptsRemainingError(Exception):
    pass


class Hint:
    pass


@dataclass
class StatHint(Hint):
    stat: Stat
    value: int


class Comparison(Enum):
    HIGHER = "higher"
    LOWER = "lower"
    EQUAL = "equal"


@dataclass
class ComparisonHint(Hint):
    pokemon: Pokemon
    comparisons: dict[Stat, Comparison]


@dataclass
class Game:
    pokemon: Pokemon
    id: str | None = None
    max_attempts: int = 4
    hints: list[Hint] = field(default_factory=list)
    attempts: list[Pokemon] = field(default_factory=list)

    def add_stat_hint(self, stat: Stat) -> StatHint:
        value = self.pokemon.get_stat(stat)
        hint = StatHint(stat=stat, value=value)
        self.hints.append(hint)
        return hint

    def add_comparison_hint(self, pokemon: Pokemon) -> ComparisonHint:
        comparisons: dict[Stat, Comparison] = {}
        for stat in Stat:
            target_value = self.pokemon.get_stat(stat)
            guess_value = pokemon.get_stat(stat)
            if target_value > guess_value:
                comparisons[stat] = Comparison.HIGHER
            elif target_value < guess_value:
                comparisons[stat] = Comparison.LOWER
            else:
                comparisons[stat] = Comparison.EQUAL

        hint = ComparisonHint(pokemon=pokemon, comparisons=comparisons)
        self.hints.append(hint)
        return hint

    @property
    def is_won(self) -> bool:
        return len(self.attempts) > 0 and self.attempts[-1].id == self.pokemon.id

    @property
    def attempts_remaining(self) -> int:
        return self.max_attempts - len(self.attempts)

    def guess(self, pokemon: Pokemon) -> bool:
        if len(self.attempts) >= self.max_attempts:
            raise NoAttemptsRemainingError()
        self.attempts.append(pokemon)
        is_correct = pokemon.id == self.pokemon.id
        if not is_correct:
            self.add_comparison_hint(pokemon)
        return is_correct
