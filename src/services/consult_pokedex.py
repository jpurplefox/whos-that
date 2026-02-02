from enum import Enum

from adapters.random_generator import RandomGenerator
from domain.exceptions import HintAlreadyRevealed, HintNotAvailable
from domain.game import Game, Hint, PrimaryTypeHint, SecondaryTypeHint, StatHint
from domain.ports.repositories import GameRepository


class HintType(Enum):
    STAT = "stat"
    PRIMARY_TYPE = "primary_type"
    SECONDARY_TYPE = "secondary_type"


class ConsultPokedex:
    def __init__(
        self,
        game_repository: GameRepository,
        random_generator: RandomGenerator,
    ):
        self.game_repository = game_repository
        self.random_generator = random_generator

    async def execute(self, game_id: str, hint_type: HintType) -> Game:
        game = await self.game_repository.get(game_id)

        hint: Hint
        cost: int | None
        match hint_type:
            case HintType.STAT:
                hint = self._create_stat_hint(game)
                cost = game.hint_costs.stat
            case HintType.PRIMARY_TYPE:
                hint = PrimaryTypeHint.create(game.pokemon)
                cost = game.hint_costs.primary_type
            case HintType.SECONDARY_TYPE:
                hint = SecondaryTypeHint.create(game.pokemon)
                cost = game.hint_costs.secondary_type

        if cost is None:
            raise HintNotAvailable()

        game.consult(hint, cost)
        return await self.game_repository.save(game)

    def _create_stat_hint(self, game: Game) -> StatHint:
        available = StatHint.available_stats(game.hints)
        if not available:
            raise HintAlreadyRevealed("All stats already revealed")
        index = self.random_generator.randint(0, len(available) - 1)
        stat = available[index]
        return StatHint.create(game.pokemon, stat)
