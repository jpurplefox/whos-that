from litestar.testing import TestClient

from api.app import app
from api.dependencies import container
from domain.user import User
from services.authenticate import AuthenticateResponse


class FakeGoogleOAuth:
    def get_authorization_url(self, state: str | None = None) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth?client_id=test"


class FakeAuthenticate:
    def __init__(self, user: User, token: str):
        self._user = user
        self._token = token

    async def execute(self, code: str) -> AuthenticateResponse:
        return AuthenticateResponse(user=self._user, token=self._token)


def test_get_google_auth_url_returns_url():
    with container.google_oauth.override(FakeGoogleOAuth()):
        with TestClient(app) as client:
            response = client.get("/auth/google/url")

    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["url"].startswith("https://accounts.google.com")


def test_google_callback_returns_token_and_user():
    user = User(
        id="user-123",
        email="test@example.com",
        google_id="google-123",
        display_name="Test User",
        avatar_url="https://example.com/avatar.png",
    )
    fake_authenticate = FakeAuthenticate(user, "jwt-token-123")

    with container.authenticate.override(fake_authenticate):
        with TestClient(app) as client:
            response = client.post(
                "/auth/google/callback",
                json={"code": "auth-code-123"},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["token"] == "jwt-token-123"
    assert data["user_id"] == "user-123"
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["avatar_url"] == "https://example.com/avatar.png"


def test_invalid_token_returns_401():
    with TestClient(app) as client:
        response = client.get(
            "/history",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
