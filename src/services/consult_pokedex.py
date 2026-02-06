from enum import Enum

from domain.exceptions import HintNotAvailable
from domain.game import Game
from domain.hint_factory import HintCreatorRegistry
from domain.ports.random_generator import RandomGenerator
from domain.ports.repositories import GameRepository


class HintType(Enum):
    STAT = "stat"
    PRIMARY_TYPE = "primary_type"
    SECONDARY_TYPE = "secondary_type"
    FULLY_EVOLVED = "fully_evolved"
    EFFECTIVENESS = "effectiveness"


class ConsultPokedex:
    def __init__(
        self,
        game_repository: GameRepository,
        random_generator: RandomGenerator,
        hint_registry: HintCreatorRegistry,
    ):
        self.game_repository = game_repository
        self.random_generator = random_generator
        self.hint_registry = hint_registry

    async def execute(self, game_id: str, hint_type: HintType) -> Game:
        game = await self.game_repository.get(game_id)

        cost: int | None = getattr(game.hint_costs, hint_type.value)
        if cost is None:
            raise HintNotAvailable()

        hint = self.hint_registry.create(
            hint_type.value, game.pokemon, game.hints, self.random_generator
        )

        game.consult(hint, cost)
        return await self.game_repository.save(game)
