import uuid
from copy import deepcopy
from datetime import datetime, timezone

from domain.exceptions import GameNotFound
from domain.game import Game


class InMemoryGameRepository:
    def __init__(self) -> None:
        self.games: dict[str, Game] = {}

    async def save(self, game: Game) -> Game:
        is_new = game.id is None
        if is_new:
            game = game.model_copy(update={
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc),
            })
        assert game.id is not None
        self.games[game.id] = deepcopy(game)
        return game

    async def get(self, game_id: str) -> Game:
        if game_id not in self.games:
            raise GameNotFound(f"Game '{game_id}' not found")
        return deepcopy(self.games[game_id])

    async def get_by_user_id(self, user_id: str) -> list[Game]:
        user_games = [
            deepcopy(game)
            for game in self.games.values()
            if game.user_id == user_id
        ]
        return sorted(user_games, key=lambda g: g.created_at or datetime.min, reverse=True)
