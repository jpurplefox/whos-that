from enum import Enum

from adapters.random_generator import RandomGenerator
from domain.exceptions import HintAlreadyRevealed
from domain.game import Game
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
        stat_cost: int,
    ):
        self.game_repository = game_repository
        self.random_generator = random_generator
        self.stat_cost = stat_cost

    async def execute(self, game_id: str, hint_type: HintType) -> Game:
        game = await self.game_repository.get(game_id)

        match hint_type:
            case HintType.STAT:
                self._consult_stat(game)
            case HintType.PRIMARY_TYPE:
                self._consult_primary_type(game)
            case HintType.SECONDARY_TYPE:
                self._consult_secondary_type(game)

        return await self.game_repository.save(game)

    def _consult_stat(self, game: Game) -> None:
        available = game.available_stats
        if not available:
            raise HintAlreadyRevealed("All stats already revealed")
        index = self.random_generator.randint(0, len(available) - 1)
        stat = available[index]
        game.consult_stat(stat, self.stat_cost)

    def _consult_primary_type(self, game: Game) -> None:
        if game.primary_type_revealed:
            raise HintAlreadyRevealed("Primary type already revealed")
        game.consult_primary_type(self.stat_cost)

    def _consult_secondary_type(self, game: Game) -> None:
        if game.secondary_type_revealed:
            raise HintAlreadyRevealed("Secondary type already revealed")
        game.consult_secondary_type(self.stat_cost)
