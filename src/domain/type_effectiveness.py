import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class EffectivenessRelation(Enum):
    WEAKNESS = "weakness"
    RESISTANCE = "resistance"
    IMMUNITY = "immunity"


class EffectivenessAttribute(BaseModel):
    relation: EffectivenessRelation
    element: str
    multiplier: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EffectivenessAttribute):
            return NotImplemented
        return (
            self.relation == other.relation
            and self.element == other.element
            and self.multiplier == other.multiplier
        )

    def __hash__(self) -> int:
        return hash((self.relation, self.element, self.multiplier))


def load_type_chart(path: Path) -> dict[tuple[str, str], float]:
    with open(path) as f:
        raw: dict[str, dict[str, float]] = json.load(f)
    return {
        (attacking, defending): multiplier
        for attacking, matchups in raw.items()
        for defending, multiplier in matchups.items()
    }


class TypeEffectiveness:
    """Calculates type effectiveness for Pokemon based on their types."""

    def __init__(self, type_chart: dict[tuple[str, str], float]) -> None:
        self._chart = type_chart

    def calculate_effectiveness(
        self, primary_type: str, secondary_type: str | None
    ) -> list[EffectivenessAttribute]:
        all_types = {
            "normal", "fire", "water", "electric", "grass", "ice",
            "fighting", "poison", "ground", "flying", "psychic", "bug",
            "rock", "ghost", "dragon", "dark", "steel", "fairy"
        }

        effectiveness_map: dict[str, float] = {}

        for attacking_type in all_types:
            multiplier = self._chart.get((attacking_type, primary_type), 1.0)

            if secondary_type:
                secondary_multiplier = self._chart.get(
                    (attacking_type, secondary_type), 1.0
                )
                multiplier *= secondary_multiplier

            effectiveness_map[attacking_type] = multiplier

        attributes = []
        for element, multiplier in effectiveness_map.items():
            if multiplier == 0.0:
                relation = EffectivenessRelation.IMMUNITY
            elif multiplier < 1.0:
                relation = EffectivenessRelation.RESISTANCE
            elif multiplier > 1.0:
                relation = EffectivenessRelation.WEAKNESS
            else:
                continue

            attributes.append(
                EffectivenessAttribute(
                    relation=relation,
                    element=element,
                    multiplier=multiplier,
                )
            )

        return attributes
