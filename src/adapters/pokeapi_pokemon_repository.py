from typing import Any

import httpx

from domain.exceptions import PokemonNotFound
from domain.pokemon import Pokemon


class PokeApiPokemonRepository:
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self.client = client
        self.base_url = base_url

    async def get_by_number(self, number: int) -> Pokemon:
        return await self._fetch_pokemon(str(number))

    async def get_by_name(self, name: str) -> Pokemon:
        return await self._fetch_pokemon(name.lower())

    async def _fetch_pokemon(self, identifier: str) -> Pokemon:
        response = await self.client.get(f"{self.base_url}/{identifier}")
        if response.status_code == 404:
            raise PokemonNotFound(f"Pokemon '{identifier}' not found")
        response.raise_for_status()
        data = response.json()
        return self._parse_pokemon(data)

    def _parse_pokemon(self, data: dict[str, Any]) -> Pokemon:
        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        types = sorted(data["types"], key=lambda t: t["slot"])
        primary_type = types[0]["type"]["name"]
        secondary_type = types[1]["type"]["name"] if len(types) > 1 else None
        return Pokemon(
            id=data["id"],
            name=data["name"],
            hp=stats["hp"],
            attack=stats["attack"],
            defense=stats["defense"],
            sp_attack=stats["special-attack"],
            sp_defense=stats["special-defense"],
            speed=stats["speed"],
            image_url=data["sprites"]["front_default"],
            primary_type=primary_type,
            secondary_type=secondary_type,
        )
