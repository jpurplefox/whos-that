from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

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


class StatHint(Hint):
    hint_type_name: ClassVar[str] = "stat"
    stat: Stat
    value: int

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(isinstance(h, StatHint) and h.stat == self.stat for h in hints)

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
    def create(cls, pokemon: Pokemon) -> "PrimaryTypeHint":
        return cls(primary_type=pokemon.primary_type)


class SecondaryTypeHint(Hint):
    hint_type_name: ClassVar[str] = "secondary_type"
    secondary_type: str | None

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(isinstance(h, SecondaryTypeHint) for h in hints)

    @classmethod
    def create(cls, pokemon: Pokemon) -> "SecondaryTypeHint":
        return cls(secondary_type=pokemon.secondary_type)


class FullyEvolvedHint(Hint):
    hint_type_name: ClassVar[str] = "fully_evolved"
    is_fully_evolved: bool

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(isinstance(h, FullyEvolvedHint) for h in hints)

    @classmethod
    def create(cls, pokemon: Pokemon) -> "FullyEvolvedHint":
        return cls(is_fully_evolved=pokemon.is_fully_evolved)


class EffectivenessHint(Hint):
    hint_type_name: ClassVar[str] = "effectiveness"
    relation: str = "completion"
    element: str | None = None
    multiplier: float | None = None

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(
            isinstance(h, EffectivenessHint)
            and h.relation == self.relation
            and h.element == self.element
            and h.multiplier == self.multiplier
            for h in hints
        )

    @classmethod
    def create(
        cls, pokemon: Pokemon, relation: str, element: str, multiplier: float
    ) -> "EffectivenessHint":
        return cls(relation=relation, element=element, multiplier=multiplier)


class MovesHint(Hint):
    hint_type_name: ClassVar[str] = "moves"
    move: str | None = None

    def is_already_revealed(self, hints: list[Hint]) -> bool:
        return any(
            isinstance(h, MovesHint) and h.move == self.move
            for h in hints
        )

    @classmethod
    def create(cls, pokemon: Pokemon, move: str) -> "MovesHint":
        return cls(move=move)


