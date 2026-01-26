from typing import Protocol

from domain.game import Game
from domain.pokemon import Pokemon


class PokemonRepository(Protocol):
    async def get_random_pokemon(self) -> Pokemon:
        ...

    async def get_by_name(self, name: str) -> Pokemon:
        ...


class GameRepository(Protocol):
    async def save(self, game: Game) -> Game:
        ...

    async def get(self, game_id: str) -> Game:
        ...
