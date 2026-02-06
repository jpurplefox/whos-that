import pytest

from adapters.in_memory_collection_repository import InMemoryCollectionRepository
from services.get_collection import GetCollection


@pytest.fixture
def collection_repository() -> InMemoryCollectionRepository:
    return InMemoryCollectionRepository()


@pytest.mark.asyncio
async def test_returns_empty_list_when_no_captures(
    collection_repository: InMemoryCollectionRepository,
) -> None:
    get_collection = GetCollection(collection_repository)

    result = await get_collection.execute("user-1")

    assert result == []


@pytest.mark.asyncio
async def test_returns_captured_pokemon_for_user(
    collection_repository: InMemoryCollectionRepository,
) -> None:
    await collection_repository.capture("user-1", 25)
    await collection_repository.capture("user-1", 4)
    get_collection = GetCollection(collection_repository)

    result = await get_collection.execute("user-1")

    pokemon_ids = {c.pokemon_id for c in result}
    assert pokemon_ids == {25, 4}


@pytest.mark.asyncio
async def test_does_not_return_pokemon_from_other_users(
    collection_repository: InMemoryCollectionRepository,
) -> None:
    await collection_repository.capture("user-1", 25)
    await collection_repository.capture("user-2", 4)
    get_collection = GetCollection(collection_repository)

    result = await get_collection.execute("user-1")

    assert len(result) == 1
    assert result[0].pokemon_id == 25
