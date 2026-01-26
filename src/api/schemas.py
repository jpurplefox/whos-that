from pydantic import BaseModel

from domain.game import ComparisonHint, Game, StatHint


class StatHintResponse(BaseModel):
    type: str = "stat"
    stat: str
    value: int


class ComparisonHintResponse(BaseModel):
    type: str = "comparison"
    pokemon: str
    comparisons: dict[str, str]


class GameResponse(BaseModel):
    id: str | None
    is_won: bool
    attempts_remaining: int
    attempts: list[str]
    hints: list[StatHintResponse | ComparisonHintResponse]

    @classmethod
    def from_game(cls, game: Game) -> "GameResponse":
        hints: list[StatHintResponse | ComparisonHintResponse] = []
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

        return cls(
            id=game.id,
            is_won=game.is_won,
            attempts_remaining=game.attempts_remaining,
            attempts=[attempt.name for attempt in game.attempts],
            hints=hints,
        )
