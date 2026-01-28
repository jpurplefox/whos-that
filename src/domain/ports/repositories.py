from typing import Protocol

from domain.game import Game
from domain.pokemon import Pokemon


class PokemonRepository(Protocol):
    async def get_by_number(self, number: int) -> Pokemon:
        ...

    async def get_by_name(self, name: str) -> Pokemon:
        ...

    async def get_all(self) -> list[Pokemon]:
        ...


class GameRepository(Protocol):
    async def save(self, game: Game) -> Game:
        ...

    async def get(self, game_id: str) -> Game:
        ...
