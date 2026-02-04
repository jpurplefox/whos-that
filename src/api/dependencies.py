import inspect
from typing import Any, TypeVar, Callable, Awaitable, Union

from litestar import Request

from api.containers import Container
from auth.google_oauth import GoogleOAuthService
from domain.exceptions import UserNotFound
from domain.ports.repositories import PokemonRepository, UserRepository
from domain.user import User
from services.authenticate import Authenticate
from services.consult_pokedex import ConsultPokedex
from services.get_game import GetGame
from services.get_history import GetHistory
from services.guess import Guess
from services.start_game import StartGame

container = Container()

T = TypeVar("T")


async def _resolve(provider: Callable[..., Union[T, Awaitable[T]]]) -> T:
    result = provider()
    if inspect.isawaitable(result):
        return await result
    return result


async def get_current_user(request: Request[Any, Any, Any]) -> User | None:
    """Extract user from JWT token if present. Returns None if no valid token."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ")
    jwt_service = await _resolve(container.jwt_service)
    payload = jwt_service.decode_token(token)

    if payload is None:
        return None

    user_repository: UserRepository = await _resolve(container.user_repository)
    try:
        user: User = await user_repository.get_by_id(payload.sub)
        return user
    except UserNotFound:
        return None


async def get_start_game() -> StartGame:
    return await _resolve(container.start_game)


async def get_guess() -> Guess:
    return await _resolve(container.guess)


async def get_get_game() -> GetGame:
    return await _resolve(container.get_game)


async def get_consult_pokedex() -> ConsultPokedex:
    return await _resolve(container.consult_pokedex)


async def get_pokemon_repository() -> PokemonRepository:
    return await _resolve(container.pokemon_repository)


async def get_google_oauth() -> GoogleOAuthService:
    return await _resolve(container.google_oauth)


async def get_authenticate() -> Authenticate:
    return await _resolve(container.authenticate)


async def get_history_use_case() -> GetHistory:
    return await _resolve(container.get_history)
