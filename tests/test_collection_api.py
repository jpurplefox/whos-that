from litestar.testing import TestClient

from api.app import app


def test_collection_returns_401_without_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/collection")

    assert response.status_code == 401
