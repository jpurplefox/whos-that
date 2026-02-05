from typing import Any

import httpx
import pytest
import respx

from adapters.pokeapi_pokemon_repository import PokeApiPokemonRepository
from domain.pokemon import Pokemon


def make_pokemon_response(
    id: int,
    name: str,
    hp: int,
    attack: int,
    defense: int,
    sp_attack: int,
    sp_defense: int,
    speed: int,
    primary_type: str,
    secondary_type: str | None = None,
    image_url: str = "https://example.com/sprite.png",
) -> dict[str, Any]:
    types = [{"slot": 1, "type": {"name": primary_type}}]
    if secondary_type:
        types.append({"slot": 2, "type": {"name": secondary_type}})
    return {
        "id": id,
        "name": name,
        "stats": [
            {"base_stat": hp, "stat": {"name": "hp"}},
            {"base_stat": attack, "stat": {"name": "attack"}},
            {"base_stat": defense, "stat": {"name": "defense"}},
            {"base_stat": sp_attack, "stat": {"name": "special-attack"}},
            {"base_stat": sp_defense, "stat": {"name": "special-defense"}},
            {"base_stat": speed, "stat": {"name": "speed"}},
        ],
        "sprites": {"front_default": image_url},
        "types": types,
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_by_number_fetches_pokemon_by_id(pikachu: Pokemon) -> None:
    respx.get("https://pokeapi.co/api/v2/pokemon/25").mock(
        return_value=httpx.Response(
            200,
            json=make_pokemon_response(
                id=25,
                name="pikachu",
                hp=35,
                attack=55,
                defense=40,
                sp_attack=50,
                sp_defense=50,
                speed=90,
                primary_type="electric",
            ),
        )
    )

    async with httpx.AsyncClient() as client:
        repository = PokeApiPokemonRepository(
            client, base_url="https://pokeapi.co/api/v2/pokemon"
        )
        pokemon = await repository.get_by_number(25)

    assert pokemon.id == pikachu.id
    assert pokemon.name == pikachu.name
    assert pokemon.primary_type == pikachu.primary_type


@pytest.mark.asyncio
@respx.mock
async def test_get_by_name_fetches_pokemon_by_name(bulbasaur: Pokemon) -> None:
    respx.get("https://pokeapi.co/api/v2/pokemon/bulbasaur").mock(
        return_value=httpx.Response(
            200,
            json=make_pokemon_response(
                id=1,
                name="bulbasaur",
                hp=45,
                attack=49,
                defense=49,
                sp_attack=65,
                sp_defense=65,
                speed=45,
                primary_type="grass",
                secondary_type="poison",
            ),
        )
    )

    async with httpx.AsyncClient() as client:
        repository = PokeApiPokemonRepository(
            client, base_url="https://pokeapi.co/api/v2/pokemon"
        )
        pokemon = await repository.get_by_name("Bulbasaur")

    assert pokemon.id == bulbasaur.id
    assert pokemon.name == bulbasaur.name
    assert pokemon.primary_type == bulbasaur.primary_type
    assert pokemon.secondary_type == bulbasaur.secondary_type
