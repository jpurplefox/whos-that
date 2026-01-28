import pytest

from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from domain.exceptions import PokemonNotFound
from domain.pokemon import Pokemon


@pytest.mark.asyncio
async def test_get_by_number_returns_pokemon():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_number(25)

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_number_raises_when_not_found():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = InMemoryPokemonRepository([pikachu])

    with pytest.raises(PokemonNotFound):
        await repository.get_by_number(999)


@pytest.mark.asyncio
async def test_get_by_name_returns_pokemon():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_name("Pikachu")

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_name_is_case_insensitive():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_name("PIKACHU")

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_name_raises_when_not_found():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = InMemoryPokemonRepository([pikachu])

    with pytest.raises(PokemonNotFound):
        await repository.get_by_name("Charmander")
