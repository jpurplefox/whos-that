import pytest

from domain.balance import Balance, HintCosts
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


@pytest.fixture
def balance() -> Balance:
    return Balance(
        max_attempts=4,
        initial_battery=100,
        max_battery=100,
        battery_recovery=10,
        hint_costs=HintCosts(stat=40, primary_type=30, secondary_type=30),
    )


@pytest.mark.asyncio
async def test_creates_game_with_pokemon(
    game_repository: GameRepository, pikachu: Pokemon, balance: Balance
):
    pokemon_selector = FakePokemonSelector(pikachu)
    stat_selector = FakeStatSelector(Stat.SPEED)

    start_game = StartGame(pokemon_selector, stat_selector, game_repository, balance)
    game = await start_game.execute()

    assert game.pokemon == pikachu


@pytest.mark.asyncio
async def test_adds_first_hint_with_selected_stat(
    game_repository: GameRepository, pikachu: Pokemon, balance: Balance
):
    pokemon_selector = FakePokemonSelector(pikachu)
    stat_selector = FakeStatSelector(Stat.SPEED)

    start_game = StartGame(pokemon_selector, stat_selector, game_repository, balance)
    game = await start_game.execute()

    assert len(game.hints) == 1
    assert game.hints[0] == StatHint(stat=Stat.SPEED, value=90)


@pytest.mark.asyncio
async def test_saves_game_with_id(
    game_repository: GameRepository, pikachu: Pokemon, balance: Balance
):
    pokemon_selector = FakePokemonSelector(pikachu)
    stat_selector = FakeStatSelector(Stat.SPEED)

    start_game = StartGame(pokemon_selector, stat_selector, game_repository, balance)
    game = await start_game.execute()

    assert game.id is not None
