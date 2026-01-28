import pytest

from adapters.in_memory_pokemon_repository import InMemoryPokemonRepository
from domain.game import Game
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.stat import Stat
from services.guess import Guess


@pytest.mark.asyncio
async def test_returns_game_with_attempt(game_repository: GameRepository):
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90, image_url="https://example.com/pikachu.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")

    pokemon_repository = InMemoryPokemonRepository([charmander])

    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)
    await game_repository.save(game)

    guess = Guess(pokemon_repository, game_repository)
    result = await guess.execute("game-1", "Charmander")

    assert len(result.attempts) == 1
    assert result.attempts[0] == charmander
