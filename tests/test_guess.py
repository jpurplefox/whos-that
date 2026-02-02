import pytest

from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from domain.game import Game, StatHint
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.stat import Stat
from services.guess import Guess


@pytest.mark.asyncio
async def test_returns_game_with_attempt(
    game_repository: GameRepository, pikachu: Pokemon, charmander: Pokemon
):
    pokemon_repository = InMemoryPokemonRepository([charmander])

    game = Game(pokemon=pikachu, id="game-1")
    game.hints.append(StatHint.create(pikachu, Stat.SPEED))
    await game_repository.save(game)

    guess = Guess(pokemon_repository, game_repository)
    result = await guess.execute("game-1", "charmander")

    assert len(result.attempts) == 1
    assert result.attempts[0] == charmander
