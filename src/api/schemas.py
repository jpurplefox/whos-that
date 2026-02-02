from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from domain.game import Game
from api.hint_serializers import hint_registry
from domain.pokemon import Pokemon


class HintTypeRequest(Enum):
    STAT = "stat"
    PRIMARY_TYPE = "primary_type"
    SECONDARY_TYPE = "secondary_type"


class ConsultRequest(BaseModel):
    hint_type: HintTypeRequest


class GuessRequest(BaseModel):
    pokemon_name: str = Field(pattern=r"^[a-zA-Z0-9-]+$", max_length=50)


class GameResponse(BaseModel):
    id: str | None
    is_won: bool
    attempts_remaining: int
    attempts: list[str]
    hints: list[dict[str, Any]]
    battery: int
    max_battery: int

    @classmethod
    def from_game(cls, game: Game) -> "GameResponse":
        return cls(
            id=game.id,
            is_won=game.is_won,
            attempts_remaining=game.attempts_remaining,
            attempts=[attempt.name for attempt in game.attempts],
            hints=[hint_registry.serialize(hint) for hint in game.hints],
            battery=game.battery,
            max_battery=game.max_battery,
        )


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
