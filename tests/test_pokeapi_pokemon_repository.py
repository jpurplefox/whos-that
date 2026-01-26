import httpx
import pytest
import respx

from domain.pokemon import Pokemon
from repositories.pokeapi_pokemon_repository import PokeApiPokemonRepository


def make_pokemon_response(
    id: int,
    name: str,
    hp: int,
    attack: int,
    defense: int,
    sp_attack: int,
    sp_defense: int,
    speed: int,
) -> dict:
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
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_by_number_fetches_pokemon_by_id():
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
            ),
        )
    )

    async with httpx.AsyncClient() as client:
        repository = PokeApiPokemonRepository(client)
        pokemon = await repository.get_by_number(25)

    assert pokemon == Pokemon(
        id=25,
        name="pikachu",
        hp=35,
        attack=55,
        defense=40,
        sp_attack=50,
        sp_defense=50,
        speed=90,
    )


@pytest.mark.asyncio
@respx.mock
async def test_get_by_name_fetches_pokemon_by_name():
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
            ),
        )
    )

    async with httpx.AsyncClient() as client:
        repository = PokeApiPokemonRepository(client)
        pokemon = await repository.get_by_name("Bulbasaur")

    assert pokemon == Pokemon(
        id=1,
        name="bulbasaur",
        hp=45,
        attack=49,
        defense=49,
        sp_attack=65,
        sp_defense=65,
        speed=45,
    )
