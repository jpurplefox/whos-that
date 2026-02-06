import json
from pathlib import Path

from pydantic import BaseModel

from domain.difficulty import DifficultyLevel


class HintCosts(BaseModel):
    stat: int | None = None
    primary_type: int | None = None
    secondary_type: int | None = None
    fully_evolved: int | None = None
    effectiveness: int | None = None


class Difficulty(BaseModel):
    max_attempts: int
    initial_battery: int
    max_battery: int
    battery_recovery: int
    hint_costs: HintCosts
    initial_hints: list[str] = []


class DifficultyConfig(BaseModel):
    difficulties: dict[DifficultyLevel, Difficulty]

    def get(self, level: DifficultyLevel) -> Difficulty:
        return self.difficulties[level]


def load_difficulty_config(path: Path) -> DifficultyConfig:
    with open(path) as f:
        data = json.load(f)
    difficulties = {
        DifficultyLevel(key): Difficulty.model_validate(value)
        for key, value in data.items()
    }
    return DifficultyConfig(difficulties=difficulties)
