import pytest

from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from domain.exceptions import PokemonNotFound
from domain.pokemon import Pokemon


@pytest.mark.asyncio
async def test_get_by_number_returns_pokemon(pikachu: Pokemon):
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_number(25)

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_number_raises_when_not_found(pikachu: Pokemon):
    repository = InMemoryPokemonRepository([pikachu])

    with pytest.raises(PokemonNotFound):
        await repository.get_by_number(999)


@pytest.mark.asyncio
async def test_get_by_name_returns_pokemon(pikachu: Pokemon):
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_name("pikachu")

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_name_is_case_insensitive(pikachu: Pokemon):
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_name("PIKACHU")

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_name_raises_when_not_found(pikachu: Pokemon):
    repository = InMemoryPokemonRepository([pikachu])

    with pytest.raises(PokemonNotFound):
        await repository.get_by_name("charmander")


@pytest.mark.asyncio
async def test_get_all_returns_all_pokemon_sorted_by_id(
    charmander: Pokemon, bulbasaur: Pokemon
):
    repository = InMemoryPokemonRepository([charmander, bulbasaur])

    result = await repository.get_all()

    assert result == [bulbasaur, charmander]
