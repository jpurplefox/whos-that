from urllib.parse import parse_qs, urlparse

import pytest
from litestar.testing import AsyncTestClient

from api.app import app
from api.dependencies import container
from domain.user import User
from services.authenticate import AuthenticateResponse


class FakeGoogleOAuth:
    def __init__(self) -> None:
        self._pending_states: set[str] = set()

    async def get_authorization_url(self) -> str:
        state = "test-state-123"
        self._pending_states.add(state)
        return "https://accounts.google.com/o/oauth2/v2/auth?client_id=test&state=" + state

    async def consume_state(self, state: str) -> bool:
        if state in self._pending_states:
            self._pending_states.discard(state)
            return True
        return False


class FakeAuthenticate:
    def __init__(self, user: User, token: str):
        self._user = user
        self._token = token

    async def execute(self, code: str) -> AuthenticateResponse:
        return AuthenticateResponse(user=self._user, token=self._token)


def _extract_state(url: str) -> str:
    return parse_qs(urlparse(url).query)["state"][0]


@pytest.mark.asyncio
async def test_get_google_auth_url_returns_url() -> None:
    with container.google_oauth.override(FakeGoogleOAuth()):
        async with AsyncTestClient(app) as client:
            response = await client.get("/api/auth/google/url")

    assert response.status_code == 200
    data = response.json()
    assert data["url"].startswith("https://accounts.google.com")
    assert "state" not in data


@pytest.mark.asyncio
async def test_google_callback_returns_token_and_user() -> None:
    user = User(
        id="user-123",
        email="test@example.com",
        provider_id="google-123",
        provider_type="google",
        display_name="Test User",
        avatar_url="https://example.com/avatar.png",
    )
    fake_oauth = FakeGoogleOAuth()
    fake_authenticate = FakeAuthenticate(user, "jwt-token-123")

    with container.google_oauth.override(fake_oauth), \
         container.authenticate.override(fake_authenticate):
        async with AsyncTestClient(app) as client:
            url_response = await client.get("/api/auth/google/url")
            state = _extract_state(url_response.json()["url"])

            response = await client.post(
                "/api/auth/google/callback",
                json={"code": "auth-code-123", "state": state},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["token"] == "jwt-token-123"
    assert data["user_id"] == "user-123"
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["avatar_url"] == "https://example.com/avatar.png"


@pytest.mark.asyncio
async def test_google_callback_rejects_invalid_state() -> None:
    fake_oauth = FakeGoogleOAuth()

    with container.google_oauth.override(fake_oauth):
        async with AsyncTestClient(app) as client:
            response = await client.post(
                "/api/auth/google/callback",
                json={"code": "auth-code-123", "state": "invalid-state"},
            )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_google_callback_rejects_reused_state() -> None:
    user = User(
        id="user-123",
        email="test@example.com",
        provider_id="google-123",
        provider_type="google",
        display_name="Test User",
        avatar_url="https://example.com/avatar.png",
    )
    fake_oauth = FakeGoogleOAuth()
    fake_authenticate = FakeAuthenticate(user, "jwt-token-123")

    with container.google_oauth.override(fake_oauth), \
         container.authenticate.override(fake_authenticate):
        async with AsyncTestClient(app) as client:
            url_response = await client.get("/api/auth/google/url")
            state = _extract_state(url_response.json()["url"])

            response1 = await client.post(
                "/api/auth/google/callback",
                json={"code": "auth-code-123", "state": state},
            )
            assert response1.status_code == 201

            response2 = await client.post(
                "/api/auth/google/callback",
                json={"code": "auth-code-123", "state": state},
            )
            assert response2.status_code == 400


@pytest.mark.asyncio
async def test_invalid_token_returns_401() -> None:
    async with AsyncTestClient(app) as client:
        response = await client.get(
            "/api/history",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
