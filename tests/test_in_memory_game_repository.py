import pytest

from adapters.in_memory_game_repository import InMemoryGameRepository
from domain.game import Game
from domain.pokemon import Pokemon


@pytest.mark.asyncio
async def test_save_assigns_id_to_new_game(pikachu: Pokemon):
    repository = InMemoryGameRepository()
    game = Game(pokemon=pikachu)

    saved_game = await repository.save(game)

    assert saved_game.id is not None


@pytest.mark.asyncio
async def test_save_preserves_existing_id(pikachu: Pokemon):
    repository = InMemoryGameRepository()
    game = Game(pokemon=pikachu, id="existing-id")

    saved_game = await repository.save(game)

    assert saved_game.id == "existing-id"


@pytest.mark.asyncio
async def test_get_returns_saved_game(pikachu: Pokemon):
    repository = InMemoryGameRepository()
    game = Game(pokemon=pikachu)
    saved_game = await repository.save(game)

    retrieved_game = await repository.get(saved_game.id)

    assert retrieved_game.id == saved_game.id
    assert retrieved_game.pokemon == pikachu


@pytest.mark.asyncio
async def test_get_returns_copy_not_reference(pikachu: Pokemon):
    repository = InMemoryGameRepository()
    game = Game(pokemon=pikachu)
    saved_game = await repository.save(game)

    retrieved_game = await repository.get(saved_game.id)
    retrieved_game.max_attempts = 10

    original_game = await repository.get(saved_game.id)
    assert original_game.max_attempts == 4


@pytest.mark.asyncio
async def test_save_stores_copy_not_reference(pikachu: Pokemon):
    repository = InMemoryGameRepository()
    game = Game(pokemon=pikachu)
    await repository.save(game)

    game.max_attempts = 10

    retrieved_game = await repository.get(game.id)
    assert retrieved_game.max_attempts == 4
