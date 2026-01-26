import pytest

from domain.game import StatHint
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.stat import Stat
from services.start_game import StartGame


class FakeStatSelector:
    def __init__(self, stat: Stat):
        self.stat = stat

    def select(self) -> Stat:
        return self.stat


class FakePokemonSelector:
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon

    async def select(self) -> Pokemon:
        return self.pokemon


@pytest.mark.asyncio
async def test_creates_game_with_pokemon(game_repository: GameRepository):
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    pokemon_selector = FakePokemonSelector(pokemon)
    stat_selector = FakeStatSelector(Stat.SPEED)

    start_game = StartGame(pokemon_selector, stat_selector, game_repository)
    game = await start_game.execute()

    assert game.pokemon == pokemon


@pytest.mark.asyncio
async def test_adds_first_hint_with_selected_stat(game_repository: GameRepository):
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    pokemon_selector = FakePokemonSelector(pokemon)
    stat_selector = FakeStatSelector(Stat.SPEED)

    start_game = StartGame(pokemon_selector, stat_selector, game_repository)
    game = await start_game.execute()

    assert len(game.hints) == 1
    assert game.hints[0] == StatHint(stat=Stat.SPEED, value=90)


@pytest.mark.asyncio
async def test_saves_game_with_id(game_repository: GameRepository):
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    pokemon_selector = FakePokemonSelector(pokemon)
    stat_selector = FakeStatSelector(Stat.SPEED)

    start_game = StartGame(pokemon_selector, stat_selector, game_repository)
    game = await start_game.execute()

    assert game.id is not None
