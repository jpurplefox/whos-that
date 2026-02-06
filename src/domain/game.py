from datetime import datetime

from pydantic import BaseModel, Field

from domain.balance import HintCosts
from domain.exceptions import (
    AlreadyConsultedThisTurn,
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

    @property
    def score(self) -> int | None:
        if not self.is_over:
            return None
        if not self.is_won:
            return 0
        return (self.attempts_remaining * 1000) + (self.battery * 10)

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
