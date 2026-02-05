import pytest

from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from adapters.random_pokemon_selector import RandomPokemonSelector
from domain.pokemon import Pokemon


class FakeRandomGenerator:
    def __init__(self, value: int):
        self.value = value

    def randint(self, min_value: int, max_value: int) -> int:
        return self.value


@pytest.mark.asyncio
async def test_select_returns_pokemon_with_random_number(pikachu: Pokemon) -> None:
    repository = InMemoryPokemonRepository([pikachu])
    random_generator = FakeRandomGenerator(25)

    selector = RandomPokemonSelector(repository, random_generator, max_pokemon_number=151)
    result = await selector.select()

    assert result == pikachu
