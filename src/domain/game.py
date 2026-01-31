from enum import Enum

from pydantic import BaseModel, Field

from domain.exceptions import AlreadyConsultedThisTurn, GameOver, NotEnoughBattery
from domain.pokemon import Pokemon
from domain.stat import Stat


class Comparison(Enum):
    HIGHER = "higher"
    LOWER = "lower"
    EQUAL = "equal"


class Hint(BaseModel):
    pass


class StatHint(Hint):
    stat: Stat
    value: int


class ComparisonHint(Hint):
    pokemon: Pokemon
    comparisons: dict[Stat, Comparison]


class PrimaryTypeHint(Hint):
    primary_type: str


class SecondaryTypeHint(Hint):
    secondary_type: str | None


class Game(BaseModel):
    model_config = {"validate_assignment": True}

    pokemon: Pokemon
    id: str | None = None
    max_attempts: int = 4
    hints: list[Hint] = Field(default_factory=list)
    attempts: list[Pokemon] = Field(default_factory=list)
    battery: int = 100
    max_battery: int = 100
    battery_recovery: int = 10
    consulted_this_turn: bool = False

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

    def add_primary_type_hint(self) -> PrimaryTypeHint:
        hint = PrimaryTypeHint(primary_type=self.pokemon.primary_type)
        self.hints.append(hint)
        return hint

    def add_secondary_type_hint(self) -> SecondaryTypeHint:
        hint = SecondaryTypeHint(secondary_type=self.pokemon.secondary_type)
        self.hints.append(hint)
        return hint

    @property
    def available_stats(self) -> list[Stat]:
        used_stats = {
            hint.stat for hint in self.hints if isinstance(hint, StatHint)
        }
        return [stat for stat in Stat if stat not in used_stats]

    @property
    def primary_type_revealed(self) -> bool:
        return any(isinstance(hint, PrimaryTypeHint) for hint in self.hints)

    @property
    def secondary_type_revealed(self) -> bool:
        return any(isinstance(hint, SecondaryTypeHint) for hint in self.hints)

    @property
    def is_over(self) -> bool:
        return self.is_won or self.attempts_remaining == 0

    def consult_stat(self, stat: Stat, cost: int) -> StatHint:
        if self.is_over:
            raise GameOver()
        if self.consulted_this_turn:
            raise AlreadyConsultedThisTurn()
        if self.battery < cost:
            raise NotEnoughBattery()
        self.battery -= cost
        self.consulted_this_turn = True
        return self.add_stat_hint(stat)

    def consult_primary_type(self, cost: int) -> PrimaryTypeHint:
        if self.is_over:
            raise GameOver()
        if self.consulted_this_turn:
            raise AlreadyConsultedThisTurn()
        if self.battery < cost:
            raise NotEnoughBattery()
        self.battery -= cost
        self.consulted_this_turn = True
        return self.add_primary_type_hint()

    def consult_secondary_type(self, cost: int) -> SecondaryTypeHint:
        if self.is_over:
            raise GameOver()
        if self.consulted_this_turn:
            raise AlreadyConsultedThisTurn()
        if self.battery < cost:
            raise NotEnoughBattery()
        self.battery -= cost
        self.consulted_this_turn = True
        return self.add_secondary_type_hint()

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
            self.add_comparison_hint(pokemon)
        self.battery = min(self.battery + self.battery_recovery, self.max_battery)
        self.consulted_this_turn = False
        return self.is_won
