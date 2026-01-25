from typing import Any, Protocol

import httpx

from domain.pokemon import Pokemon


class RandomGenerator(Protocol):
    def randint(self, min_value: int, max_value: int) -> int:
        ...


class PokeApiPokemonRepository:
    BASE_URL = "https://pokeapi.co/api/v2/pokemon"
    MAX_POKEMON_ID = 151

    def __init__(self, client: httpx.AsyncClient, random_generator: RandomGenerator):
        self.client = client
        self.random_generator = random_generator

    async def get_random_pokemon(self) -> Pokemon:
        pokemon_id = self.random_generator.randint(1, self.MAX_POKEMON_ID)
        return await self._fetch_pokemon(str(pokemon_id))

    async def get_by_name(self, name: str) -> Pokemon:
        return await self._fetch_pokemon(name.lower())

    async def _fetch_pokemon(self, identifier: str) -> Pokemon:
        response = await self.client.get(f"{self.BASE_URL}/{identifier}")
        response.raise_for_status()
        data = response.json()
        return self._parse_pokemon(data)

    def _parse_pokemon(self, data: dict[str, Any]) -> Pokemon:
        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        return Pokemon(
            id=data["id"],
            name=data["name"],
            hp=stats["hp"],
            attack=stats["attack"],
            defense=stats["defense"],
            sp_attack=stats["special-attack"],
            sp_defense=stats["special-defense"],
            speed=stats["speed"],
        )
