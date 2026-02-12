from domain.exceptions import GameAccessDenied
from domain.game import Game
from domain.ports.repositories import GameRepository


class GetGame:
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    async def execute(self, game_id: str, user_id: str | None = None) -> Game:
        game = await self.game_repository.get(game_id)
        if game.user_id is not None and user_id != game.user_id:
            raise GameAccessDenied()
        return game
