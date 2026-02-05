import pytest

from adapters.in_memory_user_repository import InMemoryUserRepository
from auth.jwt_service import JWTService
from domain.ports.oauth_provider import OAuthUserInfo
from domain.user import User
from services.authenticate import Authenticate


class FakeGoogleOAuthService:
    def __init__(self, user_info: OAuthUserInfo):
        self._user_info = user_info

    @property
    def provider_type(self) -> str:
        return "google"

    def get_authorization_url(self, state: str | None = None) -> str:
        return "https://accounts.google.com/auth"

    async def exchange_code(self, code: str) -> str:
        return "fake-access-token"

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        return self._user_info


@pytest.fixture
def oauth_user_info() -> OAuthUserInfo:
    return OAuthUserInfo(
        provider_id="google-123",
        email="test@example.com",
        name="Test User",
        picture="https://example.com/picture.png",
    )


@pytest.fixture
def fake_google_oauth(oauth_user_info: OAuthUserInfo) -> FakeGoogleOAuthService:
    return FakeGoogleOAuthService(oauth_user_info)


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
def authenticate(
    fake_google_oauth: FakeGoogleOAuthService,
    jwt_service: JWTService,
    user_repository: InMemoryUserRepository,
) -> Authenticate:
    return Authenticate(
        oauth_provider=fake_google_oauth,
        token_service=jwt_service,
        user_repository=user_repository,
    )


@pytest.mark.asyncio
async def test_creates_new_user_on_first_login(
    authenticate: Authenticate,
    user_repository: InMemoryUserRepository,
    oauth_user_info: OAuthUserInfo,
) -> None:
    result = await authenticate.execute("auth-code")

    assert result.user.email == oauth_user_info.email
    assert result.user.provider_id == oauth_user_info.provider_id
    assert result.user.provider_type == "google"
    assert result.user.display_name == oauth_user_info.name
    assert result.user.avatar_url == oauth_user_info.picture


@pytest.mark.asyncio
async def test_returns_jwt_token(
    authenticate: Authenticate,
    jwt_service: JWTService,
) -> None:
    result = await authenticate.execute("auth-code")

    payload = jwt_service.decode_token(result.token)
    assert payload is not None
    assert payload.sub == result.user.id


@pytest.mark.asyncio
async def test_updates_existing_user_on_subsequent_login(
    authenticate: Authenticate,
    user_repository: InMemoryUserRepository,
) -> None:
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
    oauth_user_info: OAuthUserInfo,
) -> None:
    await authenticate.execute("auth-code")

    saved_user = await user_repository.get_by_provider_id(oauth_user_info.provider_id, "google")
    assert saved_user is not None
    assert saved_user.email == oauth_user_info.email
