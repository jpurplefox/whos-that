import pytest

from adapters.in_memory_user_repository import InMemoryUserRepository
from auth.google_oauth import GoogleUserInfo
from auth.jwt_service import JWTService
from domain.user import User
from services.authenticate import Authenticate


class FakeGoogleOAuthService:
    def __init__(self, user_info: GoogleUserInfo):
        self._user_info = user_info

    def get_authorization_url(self, state: str | None = None) -> str:
        return "https://accounts.google.com/auth"

    async def exchange_code(self, code: str) -> str:
        return "fake-access-token"

    async def get_user_info(self, access_token: str) -> GoogleUserInfo:
        return self._user_info


@pytest.fixture
def google_user_info() -> GoogleUserInfo:
    return GoogleUserInfo(
        google_id="google-123",
        email="test@example.com",
        name="Test User",
        picture="https://example.com/picture.png",
    )


@pytest.fixture
def fake_google_oauth(google_user_info: GoogleUserInfo) -> FakeGoogleOAuthService:
    return FakeGoogleOAuthService(google_user_info)


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService(
        secret="test-secret",
        algorithm="HS256",
        expiration_hours=24,
    )


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def authenticate(
    fake_google_oauth: FakeGoogleOAuthService,
    jwt_service: JWTService,
    user_repository: InMemoryUserRepository,
) -> Authenticate:
    return Authenticate(
        google_oauth=fake_google_oauth,  # type: ignore[arg-type]
        jwt_service=jwt_service,
        user_repository=user_repository,
    )


@pytest.mark.asyncio
async def test_creates_new_user_on_first_login(
    authenticate: Authenticate,
    user_repository: InMemoryUserRepository,
    google_user_info: GoogleUserInfo,
):
    result = await authenticate.execute("auth-code")

    assert result.user.email == google_user_info.email
    assert result.user.google_id == google_user_info.google_id
    assert result.user.display_name == google_user_info.name
    assert result.user.avatar_url == google_user_info.picture


@pytest.mark.asyncio
async def test_returns_jwt_token(
    authenticate: Authenticate,
    jwt_service: JWTService,
):
    result = await authenticate.execute("auth-code")

    payload = jwt_service.decode_token(result.token)
    assert payload is not None
    assert payload.sub == result.user.id


@pytest.mark.asyncio
async def test_updates_existing_user_on_subsequent_login(
    authenticate: Authenticate,
    user_repository: InMemoryUserRepository,
):
    # First login
    first_result = await authenticate.execute("auth-code")
    user_id = first_result.user.id

    # Second login
    second_result = await authenticate.execute("auth-code")

    assert second_result.user.id == user_id
    # Should still have only one user
    users_count = len(user_repository.users)
    assert users_count == 1


@pytest.mark.asyncio
async def test_saves_user_to_repository(
    authenticate: Authenticate,
    user_repository: InMemoryUserRepository,
    google_user_info: GoogleUserInfo,
):
    await authenticate.execute("auth-code")

    saved_user = await user_repository.get_by_google_id(google_user_info.google_id)
    assert saved_user is not None
    assert saved_user.email == google_user_info.email
