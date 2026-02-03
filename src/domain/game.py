from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field

from domain.balance import HintCosts
from domain.exceptions import (
    AlreadyConsultedThisTurn,
    GameOver,
    HintAlreadyRevealed,
    NotEnoughBattery,
)
from domain.pokemon import Pokemon
from domain.stat import Stat


class Comparison(Enum):
    HIGHER = "higher"
    LOWER = "lower"
    EQUAL = "equal"


class Hint(BaseModel):
    hint_type_name: ClassVar[str]

    def is_already_revealed(self, hints: list["Hint"]) -> bool:
        raise NotImplementedError

    @classmethod
    def is_available(cls, hints: list["Hint"]) -> bool:
        raise NotImplementedError


class StatHint(Hint):
    hint_type_name: ClassVar[str] = "stat"
    stat: Stat
    value: int

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(isinstance(h, StatHint) and h.stat == self.stat for h in hints)

    @classmethod
    def is_available(cls, hints: list[Hint]) -> bool:
        return len(cls.available_stats(hints)) > 0

    @classmethod
    def create(cls, pokemon: Pokemon, stat: Stat) -> "StatHint":
        return cls(stat=stat, value=pokemon.get_stat(stat))

    @classmethod
    def available_stats(cls, hints: list[Hint]) -> list[Stat]:
        used = {h.stat for h in hints if isinstance(h, StatHint)}
        return [s for s in Stat if s not in used]


class ComparisonHint(Hint):
    pokemon: Pokemon
    comparisons: dict[Stat, Comparison]

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(
            isinstance(h, ComparisonHint) and h.pokemon.id == self.pokemon.id
            for h in hints
        )

    @classmethod
    def create(cls, target: Pokemon, guessed: Pokemon) -> "ComparisonHint":
        comparisons: dict[Stat, Comparison] = {}
        for stat in Stat:
            target_value = target.get_stat(stat)
            guess_value = guessed.get_stat(stat)
            if target_value > guess_value:
                comparisons[stat] = Comparison.HIGHER
            elif target_value < guess_value:
                comparisons[stat] = Comparison.LOWER
            else:
                comparisons[stat] = Comparison.EQUAL
        return cls(pokemon=guessed, comparisons=comparisons)


class PrimaryTypeHint(Hint):
    hint_type_name: ClassVar[str] = "primary_type"
    primary_type: str

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(isinstance(h, PrimaryTypeHint) for h in hints)

    @classmethod
    def is_available(cls, hints: list[Hint]) -> bool:
        return not any(isinstance(h, PrimaryTypeHint) for h in hints)

    @classmethod
    def create(cls, pokemon: Pokemon) -> "PrimaryTypeHint":
        return cls(primary_type=pokemon.primary_type)


class SecondaryTypeHint(Hint):
    hint_type_name: ClassVar[str] = "secondary_type"
    secondary_type: str | None

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(isinstance(h, SecondaryTypeHint) for h in hints)

    @classmethod
    def is_available(cls, hints: list[Hint]) -> bool:
        return not any(isinstance(h, SecondaryTypeHint) for h in hints)

    @classmethod
    def create(cls, pokemon: Pokemon) -> "SecondaryTypeHint":
        return cls(secondary_type=pokemon.secondary_type)


class Game(BaseModel):
    model_config = {"validate_assignment": True}

    pokemon: Pokemon
    hint_costs: HintCosts = Field(default_factory=HintCosts)
    id: str | None = None
    max_attempts: int = 4
    hints: list[Hint] = Field(default_factory=list)
    attempts: list[Pokemon] = Field(default_factory=list)
    battery: int = 100
    max_battery: int = 100
    battery_recovery: int = 10
    consulted_this_turn: bool = False

    def consult(self, hint: Hint, cost: int) -> None:
        if self.is_over:
            raise GameOver()
        if self.consulted_this_turn:
            raise AlreadyConsultedThisTurn()
        if self.battery < cost:
            raise NotEnoughBattery()
        if hint.is_already_revealed(self.hints):
            raise HintAlreadyRevealed()
        self.hints.append(hint)
        self.battery -= cost
        self.consulted_this_turn = True

    @property
    def is_over(self) -> bool:
        return self.is_won or self.attempts_remaining == 0

    @property
    def is_won(self) -> bool:
        return len(self.attempts) > 0 and self.attempts[-1].id == self.pokemon.id

    @property
    def attempts_remaining(self) -> int:
        return self.max_attempts - len(self.attempts)

    def guess(self, pokemon: Pokemon) -> bool:
        if self.is_over:
            raise GameOver()
        self.attempts.append(pokemon)
        if not self.is_won:
            hint = ComparisonHint.create(self.pokemon, pokemon)
            self.hints.append(hint)
        self.battery = min(self.battery + self.battery_recovery, self.max_battery)
        self.consulted_this_turn = False
        return self.is_won


CONSULTABLE_HINTS: list[type[Hint]] = [StatHint, PrimaryTypeHint, SecondaryTypeHint]

HINT_REGISTRY: dict[str, type[Hint]] = {h.hint_type_name: h for h in CONSULTABLE_HINTS}
