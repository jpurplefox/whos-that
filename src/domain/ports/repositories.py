from typing import Protocol

from domain.game import Game
from domain.pokemon import Pokemon
from domain.user import User


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

    async def get_by_user_id(self, user_id: str) -> list[Game]:
        ...


class UserRepository(Protocol):
    async def save(self, user: User) -> User:
        ...

    async def get_by_id(self, user_id: str) -> User:
        ...

    async def get_by_provider_id(self, provider_id: str, provider_type: str) -> User | None:
        ...
