import pytest

from adapters.in_memory_collection_repository import InMemoryCollectionRepository
from services.capture_pokemon import CapturePokemon


@pytest.fixture
def collection_repository() -> InMemoryCollectionRepository:
    return InMemoryCollectionRepository()


@pytest.mark.asyncio
async def test_capture_new_pokemon_creates_entry_with_times_caught_1(
    collection_repository: InMemoryCollectionRepository,
) -> None:
    capture = CapturePokemon(collection_repository)

    result = await capture.execute("user-1", 25)

    assert result.user_id == "user-1"
    assert result.pokemon_id == 25
    assert result.times_caught == 1
    assert result.first_caught_at is not None


@pytest.mark.asyncio
async def test_capture_existing_pokemon_increments_times_caught(
    collection_repository: InMemoryCollectionRepository,
) -> None:
    capture = CapturePokemon(collection_repository)

    await capture.execute("user-1", 25)
    result = await capture.execute("user-1", 25)

    assert result.times_caught == 2


@pytest.mark.asyncio
async def test_first_caught_at_does_not_change_on_subsequent_captures(
    collection_repository: InMemoryCollectionRepository,
) -> None:
    capture = CapturePokemon(collection_repository)

    first_capture = await capture.execute("user-1", 25)
    second_capture = await capture.execute("user-1", 25)

    assert second_capture.first_caught_at == first_capture.first_caught_at
