import pytest

from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from domain.exceptions import PokemonNotFound
from domain.pokemon import Pokemon


@pytest.mark.asyncio
async def test_get_by_number_returns_pokemon():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_number(25)

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_number_raises_when_not_found():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    repository = InMemoryPokemonRepository([pikachu])

    with pytest.raises(PokemonNotFound):
        await repository.get_by_number(999)


@pytest.mark.asyncio
async def test_get_by_name_returns_pokemon():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_name("Pikachu")

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_name_is_case_insensitive():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    repository = InMemoryPokemonRepository([pikachu])

    result = await repository.get_by_name("PIKACHU")

    assert result == pikachu


@pytest.mark.asyncio
async def test_get_by_name_raises_when_not_found():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    repository = InMemoryPokemonRepository([pikachu])

    with pytest.raises(PokemonNotFound):
        await repository.get_by_name("Charmander")


@pytest.mark.asyncio
async def test_get_all_returns_all_pokemon_sorted_by_id():
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    repository = InMemoryPokemonRepository([charmander, bulbasaur])

    result = await repository.get_all()

    assert result == [bulbasaur, charmander]
