from typing import TYPE_CHECKING, Any

from litestar.handlers import BaseRouteHandler

from auth.jwt_service import JWTService
from domain.ports.repositories import UserRepository
from domain.user import User

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection


async def get_current_user(
    connection: "ASGIConnection[Any, Any, Any, Any]",
    jwt_service: JWTService,
    user_repository: UserRepository,
) -> User | None:
    """Extract user from JWT token if present. Returns None if no valid token."""
    auth_header = connection.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    payload = jwt_service.decode_token(token)

    if payload is None:
        return None

    user = await user_repository.get_by_id(payload.sub)
    return user


def require_auth(connection: "ASGIConnection[Any, Any, Any, Any]", _: BaseRouteHandler) -> None:
    """Guard that requires authentication. Raises 401 if user is None."""
    from litestar.exceptions import NotAuthorizedException

    if connection.user is None:
        raise NotAuthorizedException("Authentication required")
