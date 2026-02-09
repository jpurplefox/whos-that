from litestar.testing import TestClient

from api.app import app


def test_history_returns_401_without_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/api/history")

    assert response.status_code == 401
