from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from dependency_injector import containers, providers
from psycopg_pool import AsyncConnectionPool

from adapters.connection_provider import (
    ConnectionProvider,
    DirectConnectionProvider,
    PoolConnectionProvider,
)
from adapters.hint_serializers import HintSerializerRegistry
from adapters.in_memory_collection_repository import InMemoryCollectionRepository
from adapters.in_memory_game_repository import InMemoryGameRepository
from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from adapters.in_memory_user_repository import InMemoryUserRepository
from adapters.pokemon_loader import load_pokemon_from_json
from adapters.postgres_collection_repository import PostgresCollectionRepository
from adapters.postgres_game_repository import PostgresGameRepository
from adapters.postgres_user_repository import PostgresUserRepository
from adapters.random_generator import SystemRandomGenerator
from adapters.random_pokemon_selector import RandomPokemonSelector
from auth.google_oauth import GoogleOAuthService
from auth.jwt_service import JWTService
from config import Settings
from domain.balance import load_difficulty_config
from domain.events import EventBus, GameWon
from services.authenticate import Authenticate
from services.capture_pokemon import CapturePokemon
from services.consult_pokedex import ConsultPokedex
from services.event_handlers import create_capture_pokemon_handler
from services.get_collection import GetCollection
from services.get_game import GetGame
from services.get_history import GetHistory
from services.guess import Guess
from services.resolve_user import ResolveUser
from services.start_game import StartGame


def _create_pokemon_repository(json_path: Path) -> InMemoryPokemonRepository:
    pokemon_list = load_pokemon_from_json(json_path)
    return InMemoryPokemonRepository(pokemon_list)


async def _create_connection_pool(
    database_url: str,
    use_pool: bool,
) -> AsyncIterator[AsyncConnectionPool | None]:
    if not database_url or not use_pool:
        yield None
        return
    pool = AsyncConnectionPool(database_url)
    await pool.open()
    try:
        yield pool
    finally:
        await pool.close()


def _create_connection_provider(
    database_url: str,
    pool: AsyncConnectionPool | None,
) -> PoolConnectionProvider | DirectConnectionProvider | None:
    if not database_url:
        return None
    if pool is not None:
        return PoolConnectionProvider(pool)
    return DirectConnectionProvider(database_url)


def _create_game_repository(
    connection_provider: ConnectionProvider | None,
    pokemon_repository: InMemoryPokemonRepository,
    hint_serializer: HintSerializerRegistry,
) -> Any:
    if connection_provider is not None:
        return PostgresGameRepository(connection_provider, pokemon_repository, hint_serializer)
    return InMemoryGameRepository()


def _create_user_repository(
    connection_provider: ConnectionProvider | None,
) -> Any:
    if connection_provider is not None:
        return PostgresUserRepository(connection_provider)
    return InMemoryUserRepository()


def _create_collection_repository(
    connection_provider: ConnectionProvider | None,
) -> Any:
    if connection_provider is not None:
        return PostgresCollectionRepository(connection_provider)
    return InMemoryCollectionRepository()


def _create_event_bus(capture_pokemon: CapturePokemon) -> EventBus:
    event_bus = EventBus()
    event_bus.subscribe(GameWon, create_capture_pokemon_handler(capture_pokemon))
    return event_bus


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    difficulty_config = providers.Singleton(
        load_difficulty_config,
        path=settings.provided.balance_json_path,
    )

    random_generator = providers.Singleton(SystemRandomGenerator)

    pokemon_repository = providers.Singleton(
        _create_pokemon_repository,
        json_path=settings.provided.pokemon_json_path,
    )

    pokemon_selector = providers.Singleton(
        RandomPokemonSelector,
        pokemon_repository=pokemon_repository,
        random_generator=random_generator,
        max_pokemon_number=settings.provided.max_pokemon_number,
    )

    connection_pool = providers.Resource(
        _create_connection_pool,
        database_url=settings.provided.database_url,
        use_pool=settings.provided.use_connection_pool,
    )

    connection_provider = providers.Singleton(
        _create_connection_provider,
        database_url=settings.provided.database_url,
        pool=connection_pool,
    )

    hint_serializer = providers.Singleton(
        HintSerializerRegistry,
        pokemon_repository=pokemon_repository,
    )

    game_repository = providers.Singleton(
        _create_game_repository,
        connection_provider=connection_provider,
        pokemon_repository=pokemon_repository,
        hint_serializer=hint_serializer,
    )

    user_repository = providers.Singleton(
        _create_user_repository,
        connection_provider=connection_provider,
    )

    collection_repository = providers.Singleton(
        _create_collection_repository,
        connection_provider=connection_provider,
    )

    jwt_service = providers.Singleton(
        JWTService,
        secret=settings.provided.jwt_secret,
        algorithm=settings.provided.jwt_algorithm,
        expiration_hours=settings.provided.jwt_expiration_hours,
    )

    google_oauth = providers.Singleton(
        GoogleOAuthService,
        client_id=settings.provided.google_client_id,
        client_secret=settings.provided.google_client_secret,
        redirect_uri=settings.provided.google_redirect_uri,
    )

    start_game = providers.Singleton(
        StartGame,
        pokemon_selector=pokemon_selector,
        random_generator=random_generator,
        game_repository=game_repository,
        difficulty_config=difficulty_config,
    )

    consult_pokedex = providers.Singleton(
        ConsultPokedex,
        game_repository=game_repository,
        random_generator=random_generator,
    )

    capture_pokemon = providers.Singleton(
        CapturePokemon,
        collection_repository=collection_repository,
    )

    event_bus = providers.Singleton(
        _create_event_bus,
        capture_pokemon=capture_pokemon,
    )

    guess = providers.Singleton(
        Guess,
        pokemon_repository=pokemon_repository,
        game_repository=game_repository,
        event_bus=event_bus,
    )

    get_collection = providers.Singleton(
        GetCollection,
        collection_repository=collection_repository,
    )

    get_game = providers.Singleton(
        GetGame,
        game_repository=game_repository,
    )

    authenticate = providers.Singleton(
        Authenticate,
        oauth_provider=google_oauth,
        token_service=jwt_service,
        user_repository=user_repository,
    )

    resolve_user = providers.Singleton(
        ResolveUser,
        token_service=jwt_service,
        user_repository=user_repository,
    )

    get_history = providers.Singleton(
        GetHistory,
        game_repository=game_repository,
    )
