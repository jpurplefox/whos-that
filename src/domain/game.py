from datetime import datetime

from pydantic import BaseModel, Field

from domain.balance import HintCosts
from domain.exceptions import (
    GameOver,
    HintAlreadyRevealed,
    NotEnoughBattery,
)
from domain.hint import ComparisonHint, Hint
from domain.pokemon import Pokemon


class Game(BaseModel):
    model_config = {"validate_assignment": True}

    pokemon: Pokemon
    hint_costs: HintCosts = Field(default_factory=HintCosts)
    id: str | None = None
    user_id: str | None = None
    created_at: datetime | None = None
    max_attempts: int = 4
    hints: list[Hint] = Field(default_factory=list)
    attempts: list[Pokemon] = Field(default_factory=list)
    battery: int = 100
    max_battery: int = 100
    battery_recovery: int = 10
    initial_battery: int = 100
    difficulty_multiplier: float = 1.0

    def consult(self, hint: Hint, cost: int) -> None:
        if self.is_over:
            raise GameOver()
        if self.battery < cost:
            raise NotEnoughBattery()
        if hint.is_already_revealed(self.hints):
            raise HintAlreadyRevealed()
        self.hints.append(hint)
        self.battery -= cost

    @property
    def is_over(self) -> bool:
        return self.is_won or self.attempts_remaining == 0

    @property
    def is_won(self) -> bool:
        return len(self.attempts) > 0 and self.attempts[-1].id == self.pokemon.id

    @property
    def attempts_remaining(self) -> int:
        return self.max_attempts - len(self.attempts)

    @property
    def score(self) -> int | None:
        if not self.is_over:
            return None
        if not self.is_won:
            return 0
        battery_pct = min(self.battery / self.initial_battery, 1.0) if self.initial_battery > 0 else 0.0
        base = 1000 + (self.attempts_remaining * 1000) + int(battery_pct * 1000)
        return int(base * self.difficulty_multiplier)

    def guess(self, pokemon: Pokemon) -> bool:
        if self.is_over:
            raise GameOver()
        self.attempts.append(pokemon)
        if not self.is_won:
            hint = ComparisonHint.create(self.pokemon, pokemon)
            self.hints.append(hint)
            self.battery = min(self.battery + self.battery_recovery, self.max_battery)
        return self.is_won
