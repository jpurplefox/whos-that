import pytest

from adapters.in_memory_collection_repository import InMemoryCollectionRepository
from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from domain.events import EventBus, GameWon
from domain.game import Game
from domain.hint import StatHint
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.stat import Stat
from services.capture_pokemon import CapturePokemon
from services.event_handlers import create_capture_pokemon_handler
from services.guess import Guess


def _create_event_bus_with_capture(
    collection_repository: InMemoryCollectionRepository,
) -> EventBus:
    capture_pokemon = CapturePokemon(collection_repository)
    event_bus = EventBus()
    event_bus.subscribe(GameWon, create_capture_pokemon_handler(capture_pokemon))
    return event_bus


@pytest.mark.asyncio
async def test_returns_game_with_attempt(
    game_repository: GameRepository,
    event_bus: EventBus,
    pikachu: Pokemon,
    charmander: Pokemon,
) -> None:
    pokemon_repository = InMemoryPokemonRepository([charmander])

    game = Game(pokemon=pikachu, id="game-1")
    game.hints.append(StatHint.create(pikachu, Stat.SPEED))
    await game_repository.save(game)

    guess = Guess(pokemon_repository, game_repository, event_bus)
    result = await guess.execute("game-1", "charmander")

    assert len(result.attempts) == 1
    assert result.attempts[0] == charmander


@pytest.mark.asyncio
async def test_captures_pokemon_when_authenticated_user_wins(
    game_repository: GameRepository, pikachu: Pokemon
) -> None:
    pokemon_repository = InMemoryPokemonRepository([pikachu])
    collection_repository = InMemoryCollectionRepository()
    event_bus = _create_event_bus_with_capture(collection_repository)

    game = Game(pokemon=pikachu, id="game-1", user_id="user-1")
    game.hints.append(StatHint.create(pikachu, Stat.SPEED))
    await game_repository.save(game)

    guess = Guess(pokemon_repository, game_repository, event_bus)
    await guess.execute("game-1", "pikachu")

    captured = await collection_repository.get_by_user_id("user-1")
    assert len(captured) == 1
    assert captured[0].pokemon.id == pikachu.id


@pytest.mark.asyncio
async def test_does_not_capture_pokemon_for_anonymous_game(
    game_repository: GameRepository, pikachu: Pokemon
) -> None:
    pokemon_repository = InMemoryPokemonRepository([pikachu])
    collection_repository = InMemoryCollectionRepository()
    event_bus = _create_event_bus_with_capture(collection_repository)

    game = Game(pokemon=pikachu, id="game-1", user_id=None)
    game.hints.append(StatHint.create(pikachu, Stat.SPEED))
    await game_repository.save(game)

    guess = Guess(pokemon_repository, game_repository, event_bus)
    await guess.execute("game-1", "pikachu")

    captured = await collection_repository.get_by_user_id("user-1")
    assert len(captured) == 0


@pytest.mark.asyncio
async def test_does_not_capture_pokemon_on_incorrect_guess(
    game_repository: GameRepository, pikachu: Pokemon, charmander: Pokemon
) -> None:
    pokemon_repository = InMemoryPokemonRepository([charmander])
    collection_repository = InMemoryCollectionRepository()
    event_bus = _create_event_bus_with_capture(collection_repository)

    game = Game(pokemon=pikachu, id="game-1", user_id="user-1")
    game.hints.append(StatHint.create(pikachu, Stat.SPEED))
    await game_repository.save(game)

    guess = Guess(pokemon_repository, game_repository, event_bus)
    await guess.execute("game-1", "charmander")

    captured = await collection_repository.get_by_user_id("user-1")
    assert len(captured) == 0
