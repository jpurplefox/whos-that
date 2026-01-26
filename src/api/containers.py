from collections.abc import AsyncIterator

import httpx
from dependency_injector import containers, providers

from config import Settings
from adapters.in_memory_game_repository import InMemoryGameRepository
from adapters.pokeapi_pokemon_repository import PokeApiPokemonRepository
from adapters.random_generator import SystemRandomGenerator
from adapters.random_pokemon_selector import RandomPokemonSelector
from adapters.random_stat_selector import RandomStatSelector
from services.guess import Guess
from services.start_game import StartGame


async def init_http_client(timeout: float) -> AsyncIterator[httpx.AsyncClient]:
    client = httpx.AsyncClient(timeout=timeout)
    yield client
    await client.aclose()


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    random_generator = providers.Singleton(SystemRandomGenerator)

    http_client = providers.Resource(
        init_http_client,
        timeout=settings.provided.http_timeout,
    )

    pokemon_repository = providers.Singleton(
        PokeApiPokemonRepository,
        client=http_client,
        base_url=settings.provided.pokeapi_base_url,
    )

    stat_selector = providers.Singleton(
        RandomStatSelector,
        random_generator=random_generator,
    )

    pokemon_selector = providers.Singleton(
        RandomPokemonSelector,
        pokemon_repository=pokemon_repository,
        random_generator=random_generator,
        max_pokemon_number=settings.provided.max_pokemon_number,
    )

    game_repository = providers.Singleton(InMemoryGameRepository)

    start_game = providers.Singleton(
        StartGame,
        pokemon_selector=pokemon_selector,
        stat_selector=stat_selector,
        game_repository=game_repository,
        max_attempts=settings.provided.max_attempts,
    )

    guess = providers.Singleton(
        Guess,
        pokemon_repository=pokemon_repository,
        game_repository=game_repository,
    )
