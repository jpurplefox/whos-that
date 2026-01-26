import httpx
from dependency_injector import containers, providers

from config import Settings
from infrastructure.random_generator import SystemRandomGenerator
from infrastructure.random_pokemon_selector import RandomPokemonSelector
from infrastructure.random_stat_selector import RandomStatSelector
from repositories.in_memory_game_repository import InMemoryGameRepository
from repositories.pokeapi_pokemon_repository import PokeApiPokemonRepository
from services.guess import Guess
from services.start_game import StartGame


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    random_generator = providers.Singleton(SystemRandomGenerator)

    http_client = providers.Singleton(
        httpx.AsyncClient,
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
