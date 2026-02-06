from datetime import datetime, timezone

from litestar.testing import TestClient

from api.app import app
from api.dependencies import container
from domain.captured_pokemon import CapturedPokemon
from domain.pokemon import Pokemon
from domain.user import User


class FakeResolveUser:
    def __init__(self, user: User):
        self._user = user

    async def execute(self, token: str) -> User:
        return self._user


class FakeGetCollection:
    def __init__(self, captured: list[CapturedPokemon]):
        self._captured = captured

    async def execute(self, user_id: str) -> list[CapturedPokemon]:
        return [c for c in self._captured if c.user_id == user_id]


def test_collection_returns_401_without_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/collection")

    assert response.status_code == 401


def test_collection_returns_empty_list_when_no_captures() -> None:
    user = User(
        id="user-1",
        email="test@example.com",
        provider_id="google-1",
        provider_type="google",
        display_name="Test User",
        avatar_url=None,
    )

    with (
        container.resolve_user.override(FakeResolveUser(user)),
        container.get_collection.override(FakeGetCollection([])),
    ):
        with TestClient(app) as client:
            response = client.get(
                "/collection",
                headers={"Authorization": "Bearer test-token"},
            )

    assert response.status_code == 200
    assert response.json() == []


def test_collection_returns_captured_pokemon(pikachu: Pokemon) -> None:
    user = User(
        id="user-1",
        email="test@example.com",
        provider_id="google-1",
        provider_type="google",
        display_name="Test User",
        avatar_url=None,
    )
    captured_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    captured = CapturedPokemon(
        user_id="user-1",
        pokemon=pikachu,
        first_caught_at=captured_at,
        times_caught=3,
    )

    with (
        container.resolve_user.override(FakeResolveUser(user)),
        container.get_collection.override(FakeGetCollection([captured])),
    ):
        with TestClient(app) as client:
            response = client.get(
                "/collection",
                headers={"Authorization": "Bearer test-token"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pokemon_id"] == pikachu.id
    assert data[0]["pokemon_name"] == pikachu.name
    assert data[0]["pokemon_image_url"] == pikachu.image_url
    assert data[0]["times_caught"] == 3
