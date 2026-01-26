import uuid
from copy import deepcopy

from domain.exceptions import GameNotFound
from domain.game import Game


class InMemoryGameRepository:
    def __init__(self) -> None:
        self.games: dict[str, Game] = {}

    async def save(self, game: Game) -> Game:
        if game.id is None:
            game.id = str(uuid.uuid4())
        self.games[game.id] = deepcopy(game)
        return game

    async def get(self, game_id: str) -> Game:
        if game_id not in self.games:
            raise GameNotFound(f"Game '{game_id}' not found")
        return deepcopy(self.games[game_id])
