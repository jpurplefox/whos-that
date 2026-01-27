from adapters.random_generator import RandomGenerator
from domain.exceptions import NoStatsAvailable
from domain.game import Game
from domain.ports.repositories import GameRepository


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

    async def execute(self, game_id: str) -> Game:
        game = await self.game_repository.get(game_id)
        available = game.available_stats
        if not available:
            raise NoStatsAvailable()
        index = self.random_generator.randint(0, len(available) - 1)
        stat = available[index]
        game.consult_stat(stat, self.stat_cost)
        return await self.game_repository.save(game)
