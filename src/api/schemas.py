from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from api.hint_serializers import hint_registry
from domain.game import Game
from domain.hint import CONSULTABLE_HINTS
from domain.pokemon import Pokemon


class DifficultyRequest(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CreateGameRequest(BaseModel):
    difficulty: DifficultyRequest = DifficultyRequest.MEDIUM


class HintTypeRequest(Enum):
    STAT = "stat"
    PRIMARY_TYPE = "primary_type"
    SECONDARY_TYPE = "secondary_type"
    FULLY_EVOLVED = "fully_evolved"
    EFFECTIVENESS = "effectiveness"


class ConsultRequest(BaseModel):
    hint_type: HintTypeRequest


class GuessRequest(BaseModel):
    pokemon_name: str = Field(pattern=r"^[a-zA-Z0-9-]+$", max_length=50)


class AvailableHint(BaseModel):
    type: str
    cost: int | None
    available: bool


class GameResponse(BaseModel):
    id: str | None
    created_at: datetime | None
    is_won: bool
    is_over: bool
    attempts_remaining: int
    attempts: list[str]
    hints: list[dict[str, Any]]
    available_hints: list[AvailableHint]
    battery: int
    max_battery: int
    battery_recovery: int
    pokemon: "PokemonResponse | None"

    @classmethod
    def from_game(cls, game: Game) -> "GameResponse":
        return cls(
            id=game.id,
            created_at=game.created_at,
            is_won=game.is_won,
            is_over=game.is_over,
            attempts_remaining=game.attempts_remaining,
            attempts=[attempt.name for attempt in game.attempts],
            hints=[hint_registry.serialize(hint) for hint in game.hints],
            available_hints=cls._build_available_hints(game),
            battery=game.battery,
            max_battery=game.max_battery,
            battery_recovery=game.battery_recovery,
            pokemon=PokemonResponse.from_pokemon(game.pokemon) if game.is_over else None,
        )

    @classmethod
    def _build_available_hints(cls, game: Game) -> list[AvailableHint]:
        result = []
        for hint_class in CONSULTABLE_HINTS:
            hint_type = hint_class.hint_type_name
            cost = getattr(game.hint_costs, hint_type)
            available = cost is not None and hint_class.is_available(game.hints)
            result.append(AvailableHint(type=hint_type, cost=cost, available=available))
        return result


class PokemonResponse(BaseModel):
    id: int
    name: str
    image_url: str

    @classmethod
    def from_pokemon(cls, pokemon: Pokemon) -> "PokemonResponse":
        return cls(
            id=pokemon.id,
            name=pokemon.name,
            image_url=pokemon.image_url,
        )


class CapturedPokemonResponse(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_image_url: str
    first_caught_at: datetime
    times_caught: int
