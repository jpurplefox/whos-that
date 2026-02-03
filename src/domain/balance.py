import json
from pathlib import Path

from pydantic import BaseModel


class HintCosts(BaseModel):
    stat: int | None = None
    primary_type: int | None = None
    secondary_type: int | None = None


class Balance(BaseModel):
    max_attempts: int
    initial_battery: int
    max_battery: int
    battery_recovery: int
    hint_costs: HintCosts
    initial_hints: list[str] = []


def load_balance(path: Path) -> Balance:
    with open(path) as f:
        data = json.load(f)
    return Balance.model_validate(data)
