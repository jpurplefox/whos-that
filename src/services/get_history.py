from domain.game import Game
from domain.ports.repositories import GameRepository


class GetHistory:
    def __init__(self, game_repository: GameRepository) -> None:
        self._game_repository = game_repository

    async def execute(self, user_id: str) -> list[Game]:
        return await self._game_repository.get_by_user_id(user_id)
