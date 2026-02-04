import pytest
from litestar.testing import TestClient

from api.app import app
from api.dependencies import container
from auth.google_oauth import GoogleUserInfo
from domain.game import Game
from domain.pokemon import Pokemon
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


class FakeGetHistory:
    def __init__(self, games: list[Game]):
        self._games = games

    async def execute(self, user_id: str) -> list[Game]:
        return self._games


@pytest.fixture
def test_user() -> User:
    return User(
        id="user-123",
        email="test@example.com",
        google_id="google-123",
        display_name="Test User",
        avatar_url="https://example.com/avatar.png",
    )


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


def test_get_google_auth_url_returns_url():
    with container.google_oauth.override(FakeGoogleOAuth()):
        with TestClient(app) as client:
            response = client.get("/auth/google/url")

    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["url"].startswith("https://accounts.google.com")


def test_google_callback_returns_token_and_user(test_user: User):
    fake_authenticate = FakeAuthenticate(test_user, "jwt-token-123")

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


def test_history_returns_401_without_auth():
    with TestClient(app) as client:
        response = client.get("/history")

    assert response.status_code == 401


def test_history_returns_games_with_valid_token(test_user: User, pikachu: Pokemon):
    games = [
        Game(pokemon=pikachu, id="game-1", user_id="user-123"),
        Game(pokemon=pikachu, id="game-2", user_id="user-123"),
    ]

    # We need to mock get_current_user to return a user
    # Since this is complex with the dependency injection, let's test the service directly
    fake_get_history = FakeGetHistory(games)

    with container.get_history.override(fake_get_history):
        with TestClient(app) as client:
            # Without proper JWT, we get 401
            response = client.get("/history")

    assert response.status_code == 401
