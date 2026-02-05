import pytest
import respx
from httpx import Response

from auth.google_oauth import GoogleOAuthService
from domain.ports.oauth_provider import OAuthUserInfo


@pytest.fixture
def google_oauth() -> GoogleOAuthService:
    return GoogleOAuthService(
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uri="http://localhost:3000/callback",
    )


def test_get_authorization_url_includes_client_id(google_oauth: GoogleOAuthService) -> None:
    url = google_oauth.get_authorization_url()

    assert "client_id=test-client-id" in url
    assert "redirect_uri=http" in url
    assert "response_type=code" in url
    assert "scope=openid" in url


def test_get_authorization_url_includes_state_when_provided(google_oauth: GoogleOAuthService) -> None:
    url = google_oauth.get_authorization_url(state="random-state")

    assert "state=random-state" in url


def test_get_authorization_url_without_state(google_oauth: GoogleOAuthService) -> None:
    url = google_oauth.get_authorization_url()

    assert "state=" not in url


@pytest.mark.asyncio
@respx.mock
async def test_exchange_code_returns_access_token(google_oauth: GoogleOAuthService) -> None:
    respx.post("https://oauth2.googleapis.com/token").mock(
        return_value=Response(
            200,
            json={
                "access_token": "ya29.test-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )
    )

    access_token = await google_oauth.exchange_code("auth-code-123")

    assert access_token == "ya29.test-access-token"


@pytest.mark.asyncio
@respx.mock
async def test_get_user_info_returns_user_info(google_oauth: GoogleOAuthService) -> None:
    respx.get("https://www.googleapis.com/oauth2/v2/userinfo").mock(
        return_value=Response(
            200,
            json={
                "id": "123456789",
                "email": "user@example.com",
                "name": "John Doe",
                "picture": "https://example.com/photo.jpg",
            },
        )
    )

    user_info = await google_oauth.get_user_info("access-token")

    assert user_info.provider_id == "123456789"
    assert user_info.email == "user@example.com"
    assert user_info.name == "John Doe"
    assert user_info.picture == "https://example.com/photo.jpg"


@pytest.mark.asyncio
@respx.mock
async def test_get_user_info_handles_missing_optional_fields(google_oauth: GoogleOAuthService) -> None:
    respx.get("https://www.googleapis.com/oauth2/v2/userinfo").mock(
        return_value=Response(
            200,
            json={
                "id": "123456789",
                "email": "user@example.com",
            },
        )
    )

    user_info = await google_oauth.get_user_info("access-token")

    assert user_info.provider_id == "123456789"
    assert user_info.email == "user@example.com"
    assert user_info.name is None
    assert user_info.picture is None
