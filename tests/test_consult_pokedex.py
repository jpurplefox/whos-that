import pytest

from domain.exceptions import HintAlreadyRevealed
from domain.game import Game
from domain.pokemon import Pokemon
from domain.ports.repositories import GameRepository
from domain.stat import Stat
from services.consult_pokedex import ConsultPokedex, HintType


class FakeRandomGenerator:
    def __init__(self, value: int = 0):
        self.value = value

    def randint(self, min_value: int, max_value: int) -> int:
        return self.value


@pytest.mark.asyncio
async def test_consult_adds_stat_hint_and_reduces_battery(
    game_repository: GameRepository, pikachu: Pokemon
):
    game = Game(pokemon=pikachu, battery=100, max_battery=100)
    game = await game_repository.save(game)

    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0), stat_cost=40)
    updated = await consult.execute(game.id, HintType.STAT)

    assert updated.battery == 60
    assert len(updated.hints) == 1
    assert updated.hints[0].stat in list(Stat)


@pytest.mark.asyncio
async def test_consult_raises_hint_already_revealed_when_all_stats_used(
    game_repository: GameRepository, pikachu: Pokemon
):
    game = Game(pokemon=pikachu, battery=100, max_battery=100)
    for stat in Stat:
        game.add_stat_hint(stat)
    game = await game_repository.save(game)

    consult = ConsultPokedex(game_repository, FakeRandomGenerator(0), stat_cost=40)

    with pytest.raises(HintAlreadyRevealed):
        await consult.execute(game.id, HintType.STAT)
