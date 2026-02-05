import pytest

from adapters.in_memory_game_repository import InMemoryGameRepository
from domain.game import Game
from domain.pokemon import Pokemon
from services.get_history import GetHistory


@pytest.fixture
def game_repository() -> InMemoryGameRepository:
    return InMemoryGameRepository()


@pytest.fixture
def get_history(game_repository: InMemoryGameRepository) -> GetHistory:
    return GetHistory(game_repository=game_repository)


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
    )


@pytest.mark.asyncio
async def test_returns_empty_list_when_no_games(get_history: GetHistory) -> None:
    games = await get_history.execute("user-123")
    assert games == []


@pytest.mark.asyncio
async def test_returns_games_for_user(
    get_history: GetHistory,
    game_repository: InMemoryGameRepository,
    pikachu: Pokemon,
) -> None:
    game = Game(pokemon=pikachu, user_id="user-123")
    await game_repository.save(game)

    games = await get_history.execute("user-123")

    assert len(games) == 1
    assert games[0].user_id == "user-123"


@pytest.mark.asyncio
async def test_does_not_return_other_users_games(
    get_history: GetHistory,
    game_repository: InMemoryGameRepository,
    pikachu: Pokemon,
) -> None:
    game1 = Game(pokemon=pikachu, user_id="user-123")
    game2 = Game(pokemon=pikachu, user_id="user-456")
    await game_repository.save(game1)
    await game_repository.save(game2)

    games = await get_history.execute("user-123")

    assert len(games) == 1
    assert games[0].user_id == "user-123"


@pytest.mark.asyncio
async def test_does_not_return_anonymous_games(
    get_history: GetHistory,
    game_repository: InMemoryGameRepository,
    pikachu: Pokemon,
) -> None:
    game_with_user = Game(pokemon=pikachu, user_id="user-123")
    game_anonymous = Game(pokemon=pikachu, user_id=None)
    await game_repository.save(game_with_user)
    await game_repository.save(game_anonymous)

    games = await get_history.execute("user-123")

    assert len(games) == 1
    assert games[0].user_id == "user-123"


@pytest.mark.asyncio
async def test_returns_multiple_games_for_user(
    get_history: GetHistory,
    game_repository: InMemoryGameRepository,
    pikachu: Pokemon,
) -> None:
    game1 = Game(pokemon=pikachu, user_id="user-123")
    game2 = Game(pokemon=pikachu, user_id="user-123")
    game3 = Game(pokemon=pikachu, user_id="user-123")
    await game_repository.save(game1)
    await game_repository.save(game2)
    await game_repository.save(game3)

    games = await get_history.execute("user-123")

    assert len(games) == 3
