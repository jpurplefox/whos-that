import pytest

from domain.balance import Balance, HintCosts
from domain.game import StatHint
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from services.start_game import StartGame


class FakeRandomGenerator:
    def __init__(self, value: int = 0):
        self.value = value

    def randint(self, min_value: int, max_value: int) -> int:
        return self.value


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
        initial_hints=["stat"],
    )


@pytest.mark.asyncio
async def test_creates_game_with_pokemon(
    game_repository: GameRepository, pikachu: Pokemon, balance: Balance
):
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(pokemon_selector, random_generator, game_repository, balance)
    game = await start_game.execute()

    assert game.pokemon == pikachu


@pytest.mark.asyncio
async def test_adds_initial_hints_from_balance(
    game_repository: GameRepository, pikachu: Pokemon, balance: Balance
):
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(pokemon_selector, random_generator, game_repository, balance)
    game = await start_game.execute()

    assert len(game.hints) == 1
    assert isinstance(game.hints[0], StatHint)


@pytest.mark.asyncio
async def test_saves_game_with_id(
    game_repository: GameRepository, pikachu: Pokemon, balance: Balance
):
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(pokemon_selector, random_generator, game_repository, balance)
    game = await start_game.execute()

    assert game.id is not None


@pytest.mark.asyncio
async def test_no_initial_hints_when_list_empty(
    game_repository: GameRepository, pikachu: Pokemon
):
    balance = Balance(
        max_attempts=4,
        initial_battery=100,
        max_battery=100,
        battery_recovery=10,
        hint_costs=HintCosts(stat=40, primary_type=30, secondary_type=30),
        initial_hints=[],
    )
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(pokemon_selector, random_generator, game_repository, balance)
    game = await start_game.execute()

    assert len(game.hints) == 0
