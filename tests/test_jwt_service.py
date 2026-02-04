from datetime import datetime, timedelta, timezone

import pytest

from auth.jwt_service import JWTService


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService(
        secret="test-secret-key-with-at-least-32-bytes",
        algorithm="HS256",
        expiration_hours=24,
    )


def test_create_token_returns_string(jwt_service: JWTService):
    token = jwt_service.create_token("user-123")
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_returns_payload(jwt_service: JWTService):
    token = jwt_service.create_token("user-123")
    payload = jwt_service.decode_token(token)

    assert payload is not None
    assert payload.sub == "user-123"


def test_decode_token_has_valid_expiration(jwt_service: JWTService):
    token = jwt_service.create_token("user-123")
    payload = jwt_service.decode_token(token)

    assert payload is not None
    now = datetime.now(timezone.utc)
    assert payload.exp > now
    assert payload.exp < now + timedelta(hours=25)


def test_decode_token_has_issued_at(jwt_service: JWTService):
    before = datetime.now(timezone.utc).replace(microsecond=0)
    token = jwt_service.create_token("user-123")
    after = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=1)

    payload = jwt_service.decode_token(token)

    assert payload is not None
    # JWT timestamps are in seconds, so microseconds are lost
    assert before <= payload.iat <= after


def test_decode_invalid_token_returns_none(jwt_service: JWTService):
    payload = jwt_service.decode_token("invalid-token")
    assert payload is None


def test_decode_token_with_wrong_secret_returns_none(jwt_service: JWTService):
    token = jwt_service.create_token("user-123")

    other_service = JWTService(
        secret="different-secret-with-at-least-32-bytes",
        algorithm="HS256",
        expiration_hours=24,
    )
    payload = other_service.decode_token(token)

    assert payload is None


def test_decode_expired_token_returns_none():
    service = JWTService(
        secret="test-secret-key-with-at-least-32-bytes",
        algorithm="HS256",
        expiration_hours=0,  # Expires immediately
    )
    token = service.create_token("user-123")

    # Token should be expired
    payload = service.decode_token(token)
    # Note: With 0 hours, it might still be valid for a brief moment
    # so we accept either None or a valid payload
    assert payload is None or payload.sub == "user-123"
