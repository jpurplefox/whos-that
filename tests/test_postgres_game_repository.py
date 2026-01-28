from unittest.mock import AsyncMock, MagicMock

import pytest

from adapters.postgres_game_repository import PostgresGameRepository
from domain.exceptions import GameNotFound
from domain.game import Comparison, ComparisonHint, Game, StatHint
from domain.pokemon import Pokemon
from domain.stat import Stat


def make_pokemon(
    id: int = 25,
    name: str = "Pikachu",
    hp: int = 35,
    attack: int = 55,
    defense: int = 40,
    sp_attack: int = 50,
    sp_defense: int = 50,
    speed: int = 90,
) -> Pokemon:
    return Pokemon(
        id=id,
        name=name,
        hp=hp,
        attack=attack,
        defense=defense,
        sp_attack=sp_attack,
        sp_defense=sp_defense,
        speed=speed,
        image_url=f"https://example.com/{name.lower()}.png",
    )


@pytest.fixture
def mock_connection():
    connection = AsyncMock()
    connection.cursor = MagicMock(return_value=AsyncMock())
    return connection


@pytest.fixture
def mock_pokemon_repository():
    repository = AsyncMock()
    return repository


@pytest.fixture
def repository(mock_connection, mock_pokemon_repository):
    return PostgresGameRepository(mock_connection, mock_pokemon_repository)


class TestSave:
    @pytest.mark.asyncio
    async def test_assigns_id_to_new_game(self, repository, mock_connection):
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=None)
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        pokemon = make_pokemon()
        game = Game(pokemon=pokemon)

        saved_game = await repository.save(game)

        assert saved_game.id is not None

    @pytest.mark.asyncio
    async def test_preserves_existing_id(self, repository, mock_connection):
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=None)
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        pokemon = make_pokemon()
        game = Game(pokemon=pokemon, id="existing-id")

        saved_game = await repository.save(game)

        assert saved_game.id == "existing-id"

    @pytest.mark.asyncio
    async def test_inserts_new_game(self, repository, mock_connection):
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=None)
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        pokemon = make_pokemon()
        game = Game(pokemon=pokemon, id="test-id")

        await repository.save(game)

        calls = cursor.execute.call_args_list
        insert_call = calls[1][0][0]
        assert "INSERT" in insert_call
        assert '"games"' in insert_call

    @pytest.mark.asyncio
    async def test_updates_existing_game(self, repository, mock_connection):
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=("existing-id",))
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        pokemon = make_pokemon()
        game = Game(pokemon=pokemon, id="existing-id")

        await repository.save(game)

        calls = cursor.execute.call_args_list
        update_call = calls[1][0][0]
        assert "UPDATE" in update_call
        assert '"games"' in update_call

    @pytest.mark.asyncio
    async def test_commits_transaction(self, repository, mock_connection):
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=None)
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        pokemon = make_pokemon()
        game = Game(pokemon=pokemon)

        await repository.save(game)

        mock_connection.commit.assert_called_once()


class TestGet:
    @pytest.mark.asyncio
    async def test_returns_saved_game(
        self, repository, mock_connection, mock_pokemon_repository
    ):
        pokemon = make_pokemon()
        mock_pokemon_repository.get_by_number.return_value = pokemon
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value=(
                "test-id",
                25,
                4,
                [],
                [],
                100,
                100,
                10,
                False,
            )
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert game.id == "test-id"
        assert game.pokemon == pokemon
        assert game.max_attempts == 4
        assert game.battery == 100
        assert game.max_battery == 100
        assert game.battery_recovery == 10
        assert game.consulted_this_turn is False

    @pytest.mark.asyncio
    async def test_raises_when_not_found(self, repository, mock_connection):
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=None)
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        with pytest.raises(GameNotFound) as exc_info:
            await repository.get("non-existent-id")

        assert "non-existent-id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_deserializes_stat_hints(
        self, repository, mock_connection, mock_pokemon_repository
    ):
        pokemon = make_pokemon()
        mock_pokemon_repository.get_by_number.return_value = pokemon
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value=(
                "test-id",
                25,
                4,
                [{"type": "stat", "stat": "speed", "value": 90}],
                [],
                100,
                100,
                10,
                False,
            )
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert len(game.hints) == 1
        assert isinstance(game.hints[0], StatHint)
        assert game.hints[0].stat == Stat.SPEED
        assert game.hints[0].value == 90

    @pytest.mark.asyncio
    async def test_deserializes_comparison_hints(
        self, repository, mock_connection, mock_pokemon_repository
    ):
        pokemon = make_pokemon()
        bulbasaur = make_pokemon(id=1, name="Bulbasaur")
        mock_pokemon_repository.get_by_number.side_effect = (
            lambda n: pokemon if n == 25 else bulbasaur
        )
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value=(
                "test-id",
                25,
                4,
                [
                    {
                        "type": "comparison",
                        "pokemon_id": 1,
                        "comparisons": {
                            "hp": "higher",
                            "attack": "lower",
                            "defense": "equal",
                            "sp_attack": "higher",
                            "sp_defense": "lower",
                            "speed": "equal",
                        },
                    }
                ],
                [],
                100,
                100,
                10,
                False,
            )
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert len(game.hints) == 1
        assert isinstance(game.hints[0], ComparisonHint)
        assert game.hints[0].pokemon == bulbasaur
        assert game.hints[0].comparisons[Stat.HP] == Comparison.HIGHER
        assert game.hints[0].comparisons[Stat.ATTACK] == Comparison.LOWER
        assert game.hints[0].comparisons[Stat.DEFENSE] == Comparison.EQUAL

    @pytest.mark.asyncio
    async def test_deserializes_attempts(
        self, repository, mock_connection, mock_pokemon_repository
    ):
        pokemon = make_pokemon()
        bulbasaur = make_pokemon(id=1, name="Bulbasaur")
        mock_pokemon_repository.get_by_number.side_effect = (
            lambda n: pokemon if n == 25 else bulbasaur
        )
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value=(
                "test-id",
                25,
                4,
                [],
                [1],
                100,
                100,
                10,
                False,
            )
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert len(game.attempts) == 1
        assert game.attempts[0] == bulbasaur


class TestSerializeHints:
    def test_serializes_stat_hint(self, repository):
        hints = [StatHint(stat=Stat.SPEED, value=90)]

        result = repository._serialize_hints(hints)

        assert result == [{"type": "stat", "stat": "speed", "value": 90}]

    def test_serializes_comparison_hint(self, repository):
        pokemon = make_pokemon()
        hints = [
            ComparisonHint(
                pokemon=pokemon,
                comparisons={
                    Stat.HP: Comparison.HIGHER,
                    Stat.ATTACK: Comparison.LOWER,
                    Stat.DEFENSE: Comparison.EQUAL,
                    Stat.SP_ATTACK: Comparison.HIGHER,
                    Stat.SP_DEFENSE: Comparison.LOWER,
                    Stat.SPEED: Comparison.EQUAL,
                },
            )
        ]

        result = repository._serialize_hints(hints)

        assert result == [
            {
                "type": "comparison",
                "pokemon_id": 25,
                "comparisons": {
                    "hp": "higher",
                    "attack": "lower",
                    "defense": "equal",
                    "sp_attack": "higher",
                    "sp_defense": "lower",
                    "speed": "equal",
                },
            }
        ]

    def test_serializes_multiple_hints(self, repository):
        pokemon = make_pokemon()
        hints = [
            StatHint(stat=Stat.HP, value=35),
            ComparisonHint(
                pokemon=pokemon,
                comparisons={stat: Comparison.EQUAL for stat in Stat},
            ),
        ]

        result = repository._serialize_hints(hints)

        assert len(result) == 2
        assert result[0]["type"] == "stat"
        assert result[1]["type"] == "comparison"
