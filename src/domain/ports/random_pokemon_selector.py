from typing import Protocol

from domain.pokemon import Pokemon


class RandomPokemonSelector(Protocol):
    async def select(self) -> Pokemon:
        ...
