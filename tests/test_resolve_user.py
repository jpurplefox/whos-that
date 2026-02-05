from datetime import datetime, timezone

import pytest

from adapters.in_memory_user_repository import InMemoryUserRepository
from auth.jwt_service import JWTService
from domain.exceptions import InvalidToken, UserNotFound
from domain.user import User
from services.resolve_user import ResolveUser


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService(
        secret="test-secret-key-with-at-least-32-bytes",
        algorithm="HS256",
        expiration_hours=24,
    )


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def resolve_user(jwt_service: JWTService, user_repository: InMemoryUserRepository) -> ResolveUser:
    return ResolveUser(token_service=jwt_service, user_repository=user_repository)


@pytest.mark.asyncio
async def test_returns_user_for_valid_token(
    resolve_user: ResolveUser,
    jwt_service: JWTService,
    user_repository: InMemoryUserRepository,
) -> None:
    user = User(
        id="user-123",
        email="test@example.com",
        provider_id="google-123",
        provider_type="google",
    )
    await user_repository.save(user)

    token = jwt_service.create_token("user-123")
    result = await resolve_user.execute(token)

    assert result.id == "user-123"
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_raises_invalid_token_for_bad_token(resolve_user: ResolveUser) -> None:
    with pytest.raises(InvalidToken):
        await resolve_user.execute("invalid-token")


@pytest.mark.asyncio
async def test_raises_user_not_found_when_user_does_not_exist(
    resolve_user: ResolveUser,
    jwt_service: JWTService,
) -> None:
    token = jwt_service.create_token("nonexistent-user")

    with pytest.raises(UserNotFound):
        await resolve_user.execute(token)
