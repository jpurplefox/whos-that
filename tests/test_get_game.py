import pytest

from domain.exceptions import GameAccessDenied
from domain.game import Game
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from services.get_game import GetGame


@pytest.mark.asyncio
async def test_get_game_returns_game(
    game_repository: GameRepository,
    pikachu: Pokemon,
) -> None:
    game = Game(pokemon=pikachu)
    saved = await game_repository.save(game)

    assert saved.id is not None
    get_game = GetGame(game_repository)
    result = await get_game.execute(saved.id)
    assert result.id == saved.id


@pytest.mark.asyncio
async def test_get_game_denies_other_user(
    game_repository: GameRepository,
    pikachu: Pokemon,
) -> None:
    game = Game(pokemon=pikachu, user_id="user-1")
    saved = await game_repository.save(game)

    assert saved.id is not None
    get_game = GetGame(game_repository)
    with pytest.raises(GameAccessDenied):
        await get_game.execute(saved.id, user_id="user-2")


@pytest.mark.asyncio
async def test_get_game_denies_anonymous_on_authenticated_game(
    game_repository: GameRepository,
    pikachu: Pokemon,
) -> None:
    game = Game(pokemon=pikachu, user_id="user-1")
    saved = await game_repository.save(game)

    assert saved.id is not None
    get_game = GetGame(game_repository)
    with pytest.raises(GameAccessDenied):
        await get_game.execute(saved.id)


@pytest.mark.asyncio
async def test_get_game_allows_owner(
    game_repository: GameRepository,
    pikachu: Pokemon,
) -> None:
    game = Game(pokemon=pikachu, user_id="user-1")
    saved = await game_repository.save(game)

    assert saved.id is not None
    get_game = GetGame(game_repository)
    result = await get_game.execute(saved.id, user_id="user-1")
    assert result.id == saved.id


@pytest.mark.asyncio
async def test_get_game_allows_anonymous_on_anonymous_game(
    game_repository: GameRepository,
    pikachu: Pokemon,
) -> None:
    game = Game(pokemon=pikachu)
    saved = await game_repository.save(game)

    assert saved.id is not None
    get_game = GetGame(game_repository)
    result = await get_game.execute(saved.id)
    assert result.id == saved.id
