from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from domain.game import ComparisonHint, Game, PrimaryTypeHint, SecondaryTypeHint, StatHint
from domain.pokemon import Pokemon


class HintTypeRequest(Enum):
    STAT = "stat"
    PRIMARY_TYPE = "primary_type"
    SECONDARY_TYPE = "secondary_type"


class ConsultRequest(BaseModel):
    hint_type: HintTypeRequest


class GuessRequest(BaseModel):
    pokemon_name: str = Field(pattern=r"^[a-zA-Z0-9-]+$", max_length=50)


class StatHintResponse(BaseModel):
    type: str = "stat"
    stat: str
    value: int


class ComparisonHintResponse(BaseModel):
    type: Literal["comparison"] = "comparison"
    pokemon: str
    comparisons: dict[str, str]


class PrimaryTypeHintResponse(BaseModel):
    type: Literal["primary_type"] = "primary_type"
    primary_type: str


class SecondaryTypeHintResponse(BaseModel):
    type: Literal["secondary_type"] = "secondary_type"
    secondary_type: str | None


HintResponse = StatHintResponse | ComparisonHintResponse | PrimaryTypeHintResponse | SecondaryTypeHintResponse


class GameResponse(BaseModel):
    id: str | None
    is_won: bool
    attempts_remaining: int
    attempts: list[str]
    hints: list[HintResponse]
    battery: int
    max_battery: int

    @classmethod
    def from_game(cls, game: Game) -> "GameResponse":
        hints: list[HintResponse] = []
        for hint in game.hints:
            if isinstance(hint, StatHint):
                hints.append(StatHintResponse(
                    stat=hint.stat.value,
                    value=hint.value,
                ))
            elif isinstance(hint, ComparisonHint):
                hints.append(ComparisonHintResponse(
                    pokemon=hint.pokemon.name,
                    comparisons={
                        stat.value: comparison.value
                        for stat, comparison in hint.comparisons.items()
                    },
                ))
            elif isinstance(hint, PrimaryTypeHint):
                hints.append(PrimaryTypeHintResponse(
                    primary_type=hint.primary_type,
                ))
            elif isinstance(hint, SecondaryTypeHint):
                hints.append(SecondaryTypeHintResponse(
                    secondary_type=hint.secondary_type,
                ))

        return cls(
            id=game.id,
            is_won=game.is_won,
            attempts_remaining=game.attempts_remaining,
            attempts=[attempt.name for attempt in game.attempts],
            hints=hints,
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
