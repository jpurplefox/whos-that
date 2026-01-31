import pytest

from adapters.in_memory_game_repository import InMemoryGameRepository
from domain.pokemon import Pokemon


@pytest.fixture
def pikachu() -> Pokemon:
    return Pokemon(
        id=25,
        name="pikachu",
        hp=35,
        attack=55,
        defense=40,
        sp_attack=50,
        sp_defense=50,
        speed=90,
        image_url="https://example.com/pikachu.png",
        primary_type="electric",
        secondary_type=None,
    )


@pytest.fixture
def bulbasaur() -> Pokemon:
    return Pokemon(
        id=1,
        name="bulbasaur",
        hp=45,
        attack=49,
        defense=49,
        sp_attack=65,
        sp_defense=65,
        speed=45,
        image_url="https://example.com/bulbasaur.png",
        primary_type="grass",
        secondary_type="poison",
    )


@pytest.fixture
def charmander() -> Pokemon:
    return Pokemon(
        id=4,
        name="charmander",
        hp=39,
        attack=52,
        defense=43,
        sp_attack=60,
        sp_defense=50,
        speed=65,
        image_url="https://example.com/charmander.png",
        primary_type="fire",
        secondary_type=None,
    )


@pytest.fixture
def game_repository():
    return InMemoryGameRepository()
