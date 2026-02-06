import pytest

from domain.balance import HintCosts
from domain.exceptions import HintAlreadyRevealed, HintNotAvailable
from domain.game import Game
from domain.hint import (
    EffectivenessHint,
    FullyEvolvedHint, Hint, StatHint
)
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.stat import Stat
from services.consult_pokedex import ConsultPokedex, HintType


class FakeRandomGenerator:
    def __init__(self, value: int = 0):
        self.value = value

    def randint(self, min_value: int, max_value: int) -> int:
        return self.value


@pytest.fixture
def hint_costs() -> HintCosts:
    return HintCosts(stat=40, primary_type=30, secondary_type=30)


@pytest.mark.asyncio
async def test_consult_adds_stat_hint_and_reduces_battery(
    game_repository: GameRepository, pikachu: Pokemon, hint_costs: HintCosts
) -> None:
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    saved_game = await game_repository.save(game)

    assert saved_game.id is not None
    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))
    updated = await consult.execute(saved_game.id, HintType.STAT)

    assert updated.battery == 60
    assert len(updated.hints) == 1
    hint = updated.hints[0]
    assert isinstance(hint, StatHint)
    assert hint.stat in list(Stat)


@pytest.mark.asyncio
async def test_consult_raises_hint_already_revealed_when_all_stats_used(
    game_repository: GameRepository, pikachu: Pokemon, hint_costs: HintCosts
) -> None:
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    for stat in Stat:
        game.hints.append(StatHint.create(pikachu, stat))
    saved_game = await game_repository.save(game)

    assert saved_game.id is not None
    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))

    with pytest.raises(HintAlreadyRevealed):
        await consult.execute(saved_game.id, HintType.STAT)


@pytest.mark.asyncio
async def test_consult_raises_hint_not_available_when_cost_is_none(
    game_repository: GameRepository, pikachu: Pokemon
) -> None:
    hint_costs = HintCosts(stat=40, primary_type=None, secondary_type=30)
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    saved_game = await game_repository.save(game)

    assert saved_game.id is not None
    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))

    with pytest.raises(HintNotAvailable):
        await consult.execute(saved_game.id, HintType.PRIMARY_TYPE)


@pytest.mark.asyncio
async def test_consult_fully_evolved_adds_hint_and_reduces_battery(
    game_repository: GameRepository, pikachu: Pokemon
) -> None:
    hint_costs = HintCosts(stat=40, fully_evolved=30)
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    saved_game = await game_repository.save(game)

    assert saved_game.id is not None
    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))
    updated = await consult.execute(saved_game.id, HintType.FULLY_EVOLVED)

    assert updated.battery == 70
    assert len(updated.hints) == 1
    assert isinstance(updated.hints[0], FullyEvolvedHint)
    assert updated.hints[0].is_fully_evolved is False


@pytest.mark.asyncio
async def test_consult_effectiveness_hint_success(
    pikachu: Pokemon,
    game_repository: GameRepository,
) -> None:
    """Test successfully consulting an effectiveness hint."""
    game = Game(pokemon=pikachu, battery=100)
    game.hint_costs.effectiveness = 20
    game = await game_repository.save(game)

    assert game.id is not None
    random_gen = FakeRandomGenerator(0)  # Select first available attribute
    consult = ConsultPokedex(game_repository, random_gen)

    result = await consult.execute(game.id, HintType.EFFECTIVENESS)

    assert result.battery == 80  # 100 - 20
    assert len(result.hints) == 1
    
    hint = result.hints[0]
    assert isinstance(hint, EffectivenessHint)
    assert hint.element in ["ground", "electric", "flying", "steel"]  # Pikachu's non-neutral types
    assert hint.multiplier != 1.0  # Should not be neutral


@pytest.mark.asyncio
async def test_consult_effectiveness_does_not_repeat(
    pikachu: Pokemon,
    game_repository: GameRepository,
) -> None:
    """Test that effectiveness hints are not repeated."""
    game = Game(pokemon=pikachu, battery=100)
    game.hint_costs.effectiveness = 10
    
    # Pre-reveal ground weakness
    ground_hint = EffectivenessHint(
        relation="weakness", element="ground", multiplier=2.0
    )
    game.hints.append(ground_hint)
    game = await game_repository.save(game)

    assert game.id is not None
    random_gen = FakeRandomGenerator(0)
    consult = ConsultPokedex(game_repository, random_gen)

    result = await consult.execute(game.id, HintType.EFFECTIVENESS)

    # Should get a different effectiveness attribute
    new_hint = result.hints[-1]
    assert isinstance(new_hint, EffectivenessHint)
    assert not (
        new_hint.relation == "weakness"
        and new_hint.element == "ground"
        and new_hint.multiplier == 2.0
    )


@pytest.mark.asyncio
async def test_consult_effectiveness_completion_hint(
    pikachu: Pokemon,
    game_repository: GameRepository,
) -> None:
    """Test that a completion hint is returned after all individual attributes are revealed."""
    game = Game(pokemon=pikachu, battery=100)
    game.hint_costs.effectiveness = 10

    # Reveal all individual effectiveness attributes
    all_attributes = EffectivenessHint.unrevealed_effectiveness(pikachu, [])
    for attr in all_attributes:
        hint = EffectivenessHint(
            relation=attr.relation.value,
            element=attr.element,
            multiplier=attr.multiplier,
        )
        game.hints.append(hint)

    game = await game_repository.save(game)

    assert game.id is not None
    random_gen = FakeRandomGenerator(0)
    consult = ConsultPokedex(game_repository, random_gen)

    result = await consult.execute(game.id, HintType.EFFECTIVENESS)

    completion = result.hints[-1]
    assert isinstance(completion, EffectivenessHint)
    assert completion.element is None
    assert completion.multiplier is None


@pytest.mark.asyncio
async def test_consult_effectiveness_all_exhausted(
    pikachu: Pokemon,
    game_repository: GameRepository,
) -> None:
    """Test that consulting fails when all effectiveness attributes and completion are revealed."""
    game = Game(pokemon=pikachu, battery=100)
    game.hint_costs.effectiveness = 10

    # Reveal all individual effectiveness attributes
    all_attributes = EffectivenessHint.unrevealed_effectiveness(pikachu, [])
    for attr in all_attributes:
        hint = EffectivenessHint(
            relation=attr.relation.value,
            element=attr.element,
            multiplier=attr.multiplier,
        )
        game.hints.append(hint)

    # Also reveal the completion hint
    game.hints.append(EffectivenessHint())

    game = await game_repository.save(game)

    assert game.id is not None
    random_gen = FakeRandomGenerator(0)
    consult = ConsultPokedex(game_repository, random_gen)

    # Should raise HintAlreadyRevealed
    with pytest.raises(HintAlreadyRevealed):
        await consult.execute(game.id, HintType.EFFECTIVENESS)


@pytest.mark.asyncio
async def test_consult_effectiveness_dual_type_pokemon(
    bulbasaur: Pokemon,
    game_repository: GameRepository,
) -> None:
    """Test effectiveness hints work for dual-type Pokemon."""
    game = Game(pokemon=bulbasaur, battery=100)
    game.hint_costs.effectiveness = 15
    game = await game_repository.save(game)

    assert game.id is not None
    random_gen = FakeRandomGenerator(0)
    consult = ConsultPokedex(game_repository, random_gen)

    result = await consult.execute(game.id, HintType.EFFECTIVENESS)

    assert len(result.hints) == 1
    hint = result.hints[0]
    assert isinstance(hint, EffectivenessHint)
    # Bulbasaur (Grass/Poison) should have effectiveness attributes
    assert hint.multiplier != 1.0


@pytest.mark.asyncio
async def test_consult_effectiveness_cost_none_raises_not_available(
    pikachu: Pokemon,
    game_repository: GameRepository,
) -> None:
    """Test that consulting fails when effectiveness cost is None."""
    game = Game(pokemon=pikachu, battery=100)
    game.hint_costs.effectiveness = None  # Not available in this difficulty
    game = await game_repository.save(game)

    assert game.id is not None
    random_gen = FakeRandomGenerator(0)
    consult = ConsultPokedex(game_repository, random_gen)

    with pytest.raises(HintNotAvailable):
        await consult.execute(game.id, HintType.EFFECTIVENESS)
