import pytest

from adapters.in_memory_user_repository import InMemoryUserRepository
from domain.exceptions import UserNotFound
from domain.user import User


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def sample_user() -> User:
    return User(
        id="",
        email="test@example.com",
        provider_id="google-123",
        provider_type="google",
        display_name="Test User",
        avatar_url="https://example.com/avatar.png",
    )


@pytest.mark.asyncio
async def test_save_assigns_id_to_new_user(
    user_repository: InMemoryUserRepository,
    sample_user: User,
) -> None:
    sample_user.id = ""
    saved_user = await user_repository.save(sample_user)

    assert saved_user.id != ""
    assert len(saved_user.id) > 0


@pytest.mark.asyncio
async def test_save_preserves_existing_id(
    user_repository: InMemoryUserRepository,
    sample_user: User,
) -> None:
    sample_user.id = "existing-id"
    saved_user = await user_repository.save(sample_user)

    assert saved_user.id == "existing-id"


@pytest.mark.asyncio
async def test_save_sets_timestamps(
    user_repository: InMemoryUserRepository,
    sample_user: User,
) -> None:
    saved_user = await user_repository.save(sample_user)

    assert saved_user.created_at is not None
    assert saved_user.updated_at is not None


@pytest.mark.asyncio
async def test_get_by_id_returns_user(
    user_repository: InMemoryUserRepository,
    sample_user: User,
) -> None:
    saved_user = await user_repository.save(sample_user)
    retrieved_user = await user_repository.get_by_id(saved_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == saved_user.id
    assert retrieved_user.email == sample_user.email


@pytest.mark.asyncio
async def test_get_by_id_raises_when_not_found(
    user_repository: InMemoryUserRepository,
) -> None:
    with pytest.raises(UserNotFound):
        await user_repository.get_by_id("nonexistent")


@pytest.mark.asyncio
async def test_get_by_provider_id_returns_user(
    user_repository: InMemoryUserRepository,
    sample_user: User,
) -> None:
    await user_repository.save(sample_user)
    retrieved_user = await user_repository.get_by_provider_id(
        sample_user.provider_id, sample_user.provider_type
    )

    assert retrieved_user is not None
    assert retrieved_user.provider_id == sample_user.provider_id
    assert retrieved_user.provider_type == sample_user.provider_type


@pytest.mark.asyncio
async def test_get_by_provider_id_returns_none_when_not_found(
    user_repository: InMemoryUserRepository,
) -> None:
    user = await user_repository.get_by_provider_id("nonexistent", "google")
    assert user is None
