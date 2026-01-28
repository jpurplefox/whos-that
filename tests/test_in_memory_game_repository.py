import pytest

from domain.game import Game
from domain.pokemon import Pokemon
from adapters.in_memory_game_repository import InMemoryGameRepository


@pytest.mark.asyncio
async def test_save_assigns_id_to_new_game():
    repository = InMemoryGameRepository()
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    game = Game(pokemon=pokemon)

    saved_game = await repository.save(game)

    assert saved_game.id is not None


@pytest.mark.asyncio
async def test_save_preserves_existing_id():
    repository = InMemoryGameRepository()
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    game = Game(pokemon=pokemon, id="existing-id")

    saved_game = await repository.save(game)

    assert saved_game.id == "existing-id"


@pytest.mark.asyncio
async def test_get_returns_saved_game():
    repository = InMemoryGameRepository()
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    game = Game(pokemon=pokemon)
    saved_game = await repository.save(game)

    retrieved_game = await repository.get(saved_game.id)

    assert retrieved_game.id == saved_game.id
    assert retrieved_game.pokemon == pokemon


@pytest.mark.asyncio
async def test_get_returns_copy_not_reference():
    repository = InMemoryGameRepository()
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    game = Game(pokemon=pokemon)
    saved_game = await repository.save(game)

    retrieved_game = await repository.get(saved_game.id)
    retrieved_game.max_attempts = 10

    original_game = await repository.get(saved_game.id)
    assert original_game.max_attempts == 4


@pytest.mark.asyncio
async def test_save_stores_copy_not_reference():
    repository = InMemoryGameRepository()
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    game = Game(pokemon=pokemon)
    await repository.save(game)

    game.max_attempts = 10

    retrieved_game = await repository.get(game.id)
    assert retrieved_game.max_attempts == 4
