from domain.game import Game
from domain.ports.repositories import GameRepository


class GetGame:
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    async def execute(self, game_id: str) -> Game:
        return await self.game_repository.get(game_id)
