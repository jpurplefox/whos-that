from pathlib import Path

from dependency_injector import containers, providers

from adapters.in_memory_game_repository import InMemoryGameRepository
from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from adapters.pokemon_loader import load_pokemon_from_json
from adapters.random_generator import SystemRandomGenerator
from adapters.random_pokemon_selector import RandomPokemonSelector
from adapters.random_stat_selector import RandomStatSelector
from config import Settings
from services.consult_pokedex import ConsultPokedex
from services.get_game import GetGame
from services.guess import Guess
from services.start_game import StartGame


def _create_pokemon_repository(json_path: Path) -> InMemoryPokemonRepository:
    pokemon_list = load_pokemon_from_json(json_path)
    return InMemoryPokemonRepository(pokemon_list)


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    random_generator = providers.Singleton(SystemRandomGenerator)

    pokemon_repository = providers.Singleton(
        _create_pokemon_repository,
        json_path=settings.provided.pokemon_json_path,
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
        max_battery=settings.provided.pokedex_max_battery,
        battery_recovery=settings.provided.pokedex_battery_recovery,
    )

    consult_pokedex = providers.Singleton(
        ConsultPokedex,
        game_repository=game_repository,
        random_generator=random_generator,
        stat_cost=settings.provided.pokedex_stat_cost,
    )

    guess = providers.Singleton(
        Guess,
        pokemon_repository=pokemon_repository,
        game_repository=game_repository,
    )

    get_game = providers.Singleton(
        GetGame,
        game_repository=game_repository,
    )
