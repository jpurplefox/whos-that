import pytest

from domain.balance import HintCosts
from domain.exceptions import HintAlreadyRevealed, HintNotAvailable
from domain.game import Game, StatHint
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
):
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    game = await game_repository.save(game)

    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))
    updated = await consult.execute(game.id, HintType.STAT)

    assert updated.battery == 60
    assert len(updated.hints) == 1
    assert updated.hints[0].stat in list(Stat)


@pytest.mark.asyncio
async def test_consult_raises_hint_already_revealed_when_all_stats_used(
    game_repository: GameRepository, pikachu: Pokemon, hint_costs: HintCosts
):
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    for stat in Stat:
        game.hints.append(StatHint.create(pikachu, stat))
    game = await game_repository.save(game)

    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))

    with pytest.raises(HintAlreadyRevealed):
        await consult.execute(game.id, HintType.STAT)


@pytest.mark.asyncio
async def test_consult_raises_hint_not_available_when_cost_is_none(
    game_repository: GameRepository, pikachu: Pokemon
):
    hint_costs = HintCosts(stat=40, primary_type=None, secondary_type=30)
    game = Game(pokemon=pikachu, hint_costs=hint_costs, battery=100, max_battery=100)
    game = await game_repository.save(game)

    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0))

    with pytest.raises(HintNotAvailable):
        await consult.execute(game.id, HintType.PRIMARY_TYPE)
