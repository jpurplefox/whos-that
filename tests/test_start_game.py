import pytest

from domain.balance import Difficulty, DifficultyConfig, HintCosts
from domain.difficulty import DifficultyLevel
from domain.hint import StatHint
from domain.hint_factory import HintCreatorRegistry, create_hint_registry
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.type_effectiveness import TypeEffectiveness
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


def _create_difficulty_config(difficulty: Difficulty) -> DifficultyConfig:
    return DifficultyConfig(difficulties={DifficultyLevel.MEDIUM: difficulty})


@pytest.fixture
def hint_registry(type_effectiveness: TypeEffectiveness) -> HintCreatorRegistry:
    return create_hint_registry(type_effectiveness)


@pytest.fixture
def difficulty_config() -> DifficultyConfig:
    difficulty = Difficulty(
        max_attempts=4,
        initial_battery=100,
        max_battery=100,
        battery_recovery=10,
        hint_costs=HintCosts(stat=40, primary_type=30, secondary_type=30),
        initial_hints=["stat"],
    )
    return _create_difficulty_config(difficulty)


@pytest.mark.asyncio
async def test_creates_game_with_pokemon(
    game_repository: GameRepository, pikachu: Pokemon, difficulty_config: DifficultyConfig,
    hint_registry: HintCreatorRegistry,
) -> None:
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(
        pokemon_selector, random_generator, game_repository, difficulty_config, hint_registry
    )
    game = await start_game.execute()

    assert game.pokemon == pikachu


@pytest.mark.asyncio
async def test_adds_initial_hints_from_difficulty(
    game_repository: GameRepository, pikachu: Pokemon, difficulty_config: DifficultyConfig,
    hint_registry: HintCreatorRegistry,
) -> None:
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(
        pokemon_selector, random_generator, game_repository, difficulty_config, hint_registry
    )
    game = await start_game.execute()

    assert len(game.hints) == 1
    assert isinstance(game.hints[0], StatHint)


@pytest.mark.asyncio
async def test_saves_game_with_id(
    game_repository: GameRepository, pikachu: Pokemon, difficulty_config: DifficultyConfig,
    hint_registry: HintCreatorRegistry,
) -> None:
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(
        pokemon_selector, random_generator, game_repository, difficulty_config, hint_registry
    )
    game = await start_game.execute()

    assert game.id is not None


@pytest.mark.asyncio
async def test_no_initial_hints_when_list_empty(
    game_repository: GameRepository, pikachu: Pokemon,
    hint_registry: HintCreatorRegistry,
) -> None:
    difficulty = Difficulty(
        max_attempts=4,
        initial_battery=100,
        max_battery=100,
        battery_recovery=10,
        hint_costs=HintCosts(stat=40, primary_type=30, secondary_type=30),
        initial_hints=[],
    )
    difficulty_config = _create_difficulty_config(difficulty)
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(
        pokemon_selector, random_generator, game_repository, difficulty_config, hint_registry
    )
    game = await start_game.execute()

    assert len(game.hints) == 0


@pytest.mark.asyncio
async def test_creates_game_with_easy_difficulty(
    game_repository: GameRepository, pikachu: Pokemon,
    hint_registry: HintCreatorRegistry,
) -> None:
    easy_difficulty = Difficulty(
        max_attempts=6,
        initial_battery=150,
        max_battery=150,
        battery_recovery=35,
        hint_costs=HintCosts(stat=30),
        initial_hints=["stat", "stat"],
    )
    difficulty_config = DifficultyConfig(difficulties={DifficultyLevel.EASY: easy_difficulty})
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(
        pokemon_selector, random_generator, game_repository, difficulty_config, hint_registry
    )
    game = await start_game.execute(DifficultyLevel.EASY)

    assert game.max_attempts == 6
    assert game.battery == 150
    assert game.max_battery == 150
    assert game.battery_recovery == 35
    assert len(game.hints) == 2


@pytest.mark.asyncio
async def test_creates_game_with_hard_difficulty(
    game_repository: GameRepository, pikachu: Pokemon,
    hint_registry: HintCreatorRegistry,
) -> None:
    hard_difficulty = Difficulty(
        max_attempts=3,
        initial_battery=60,
        max_battery=60,
        battery_recovery=15,
        hint_costs=HintCosts(stat=50),
        initial_hints=[],
    )
    difficulty_config = DifficultyConfig(difficulties={DifficultyLevel.HARD: hard_difficulty})
    pokemon_selector = FakePokemonSelector(pikachu)
    random_generator = FakeRandomGenerator(0)

    start_game = StartGame(
        pokemon_selector, random_generator, game_repository, difficulty_config, hint_registry
    )
    game = await start_game.execute(DifficultyLevel.HARD)

    assert game.max_attempts == 3
    assert game.battery == 60
    assert game.max_battery == 60
    assert game.battery_recovery == 15
    assert len(game.hints) == 0
