from unittest.mock import AsyncMock, MagicMock

import pytest

from adapters.hint_serializers import HintSerializerRegistry
from adapters.postgres_game_repository import PostgresGameRepository
from domain.exceptions import GameNotFound
from domain.game import Game
from domain.hint import Comparison, ComparisonHint, Hint, StatHint
from domain.pokemon import Pokemon
from domain.stat import Stat


@pytest.fixture
def mock_connection_provider() -> MagicMock:
    provider = MagicMock()
    connection = AsyncMock()
    connection.cursor = MagicMock(return_value=AsyncMock())
    provider.connection.return_value.__aenter__.return_value = connection
    return provider


@pytest.fixture
def mock_connection(mock_connection_provider: MagicMock) -> AsyncMock:
    conn: AsyncMock = mock_connection_provider.connection.return_value.__aenter__.return_value
    return conn


@pytest.fixture
def mock_pokemon_repository() -> AsyncMock:
    repository = AsyncMock()
    return repository


@pytest.fixture
def hint_serializer(mock_pokemon_repository: AsyncMock) -> HintSerializerRegistry:
    return HintSerializerRegistry(mock_pokemon_repository)


@pytest.fixture
def repository(
    mock_connection_provider: MagicMock,
    mock_pokemon_repository: AsyncMock,
    hint_serializer: HintSerializerRegistry,
) -> PostgresGameRepository:
    return PostgresGameRepository(mock_connection_provider, mock_pokemon_repository, hint_serializer)


class TestSave:
    @pytest.mark.asyncio
    async def test_assigns_id_to_new_game(
        self, repository: PostgresGameRepository, mock_connection: AsyncMock, pikachu: Pokemon
    ) -> None:
        cursor = AsyncMock()
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        game = Game(pokemon=pikachu)

        saved_game = await repository.save(game)

        assert saved_game.id is not None

    @pytest.mark.asyncio
    async def test_preserves_existing_id(
        self, repository: PostgresGameRepository, mock_connection: AsyncMock, pikachu: Pokemon
    ) -> None:
        cursor = AsyncMock()
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        game = Game(pokemon=pikachu, id="existing-id")

        saved_game = await repository.save(game)

        assert saved_game.id == "existing-id"

    @pytest.mark.asyncio
    async def test_executes_upsert_query(
        self, repository: PostgresGameRepository, mock_connection: AsyncMock, pikachu: Pokemon
    ) -> None:
        cursor = AsyncMock()
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        game = Game(pokemon=pikachu, id="test-id")

        await repository.save(game)

        calls = cursor.execute.call_args_list
        upsert_call = calls[0][0][0]
        assert "INSERT" in upsert_call
        assert "ON CONFLICT" in upsert_call
        assert '"games"' in upsert_call

    @pytest.mark.asyncio
    async def test_commits_transaction(
        self, repository: PostgresGameRepository, mock_connection: AsyncMock, pikachu: Pokemon
    ) -> None:
        cursor = AsyncMock()
        mock_connection.cursor.return_value.__aenter__.return_value = cursor
        game = Game(pokemon=pikachu)

        await repository.save(game)

        mock_connection.commit.assert_called_once()


class TestGet:
    @pytest.mark.asyncio
    async def test_returns_saved_game(
        self,
        repository: PostgresGameRepository,
        mock_connection: AsyncMock,
        mock_pokemon_repository: AsyncMock,
        pikachu: Pokemon,
    ) -> None:
        mock_pokemon_repository.get_by_number.return_value = pikachu
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value={
                "id": "test-id",
                "pokemon_id": 25,
                "max_attempts": 4,
                "hints": [],
                "attempts": [],
                "battery": 100,
                "max_battery": 100,
                "battery_recovery": 10,
                "hint_costs": None,
                "initial_battery": 100,
                "difficulty_multiplier": 1.0,
            }
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert game.id == "test-id"
        assert game.pokemon == pikachu
        assert game.max_attempts == 4
        assert game.battery == 100
        assert game.max_battery == 100
        assert game.battery_recovery == 10
        assert game.initial_battery == 100
        assert game.difficulty_multiplier == 1.0

    @pytest.mark.asyncio
    async def test_handles_null_scoring_fields(
        self,
        repository: PostgresGameRepository,
        mock_connection: AsyncMock,
        mock_pokemon_repository: AsyncMock,
        pikachu: Pokemon,
    ) -> None:
        mock_pokemon_repository.get_by_number.return_value = pikachu
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value={
                "id": "test-id",
                "pokemon_id": 25,
                "max_attempts": 4,
                "hints": [],
                "attempts": [],
                "battery": 100,
                "max_battery": 100,
                "battery_recovery": 10,
                "hint_costs": None,
                "initial_battery": None,
                "difficulty_multiplier": None,
            }
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert game.initial_battery == 100
        assert game.difficulty_multiplier == 1.0

    @pytest.mark.asyncio
    async def test_raises_when_not_found(
        self, repository: PostgresGameRepository, mock_connection: AsyncMock
    ) -> None:
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(return_value=None)
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        with pytest.raises(GameNotFound) as exc_info:
            await repository.get("non-existent-id")

        assert "non-existent-id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_deserializes_stat_hints(
        self,
        repository: PostgresGameRepository,
        mock_connection: AsyncMock,
        mock_pokemon_repository: AsyncMock,
        pikachu: Pokemon,
    ) -> None:
        mock_pokemon_repository.get_by_number.return_value = pikachu
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value={
                "id": "test-id",
                "pokemon_id": 25,
                "max_attempts": 4,
                "hints": [{"type": "stat", "stat": "speed", "value": 90}],
                "attempts": [],
                "battery": 100,
                "max_battery": 100,
                "battery_recovery": 10,
                "hint_costs": None,
                "initial_battery": 100,
                "difficulty_multiplier": 1.0,
            }
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert len(game.hints) == 1
        assert isinstance(game.hints[0], StatHint)
        assert game.hints[0].stat == Stat.SPEED
        assert game.hints[0].value == 90

    @pytest.mark.asyncio
    async def test_deserializes_comparison_hints(
        self,
        repository: PostgresGameRepository,
        mock_connection: AsyncMock,
        mock_pokemon_repository: AsyncMock,
        pikachu: Pokemon,
        bulbasaur: Pokemon,
    ) -> None:
        mock_pokemon_repository.get_by_number.side_effect = (
            lambda n: pikachu if n == 25 else bulbasaur
        )
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value={
                "id": "test-id",
                "pokemon_id": 25,
                "max_attempts": 4,
                "hints": [
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
                "attempts": [],
                "battery": 100,
                "max_battery": 100,
                "battery_recovery": 10,
                "hint_costs": None,
                "initial_battery": 100,
                "difficulty_multiplier": 1.0,
            }
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
        self,
        repository: PostgresGameRepository,
        mock_connection: AsyncMock,
        mock_pokemon_repository: AsyncMock,
        pikachu: Pokemon,
        bulbasaur: Pokemon,
    ) -> None:
        mock_pokemon_repository.get_by_number.side_effect = (
            lambda n: pikachu if n == 25 else bulbasaur
        )
        cursor = AsyncMock()
        cursor.fetchone = AsyncMock(
            return_value={
                "id": "test-id",
                "pokemon_id": 25,
                "max_attempts": 4,
                "hints": [],
                "attempts": [1],
                "battery": 100,
                "max_battery": 100,
                "battery_recovery": 10,
                "hint_costs": None,
                "initial_battery": 100,
                "difficulty_multiplier": 1.0,
            }
        )
        mock_connection.cursor.return_value.__aenter__.return_value = cursor

        game = await repository.get("test-id")

        assert len(game.attempts) == 1
        assert game.attempts[0] == bulbasaur


class TestSerializeHints:
    def test_serializes_stat_hint(self, repository: PostgresGameRepository) -> None:
        hints: list[Hint] = [StatHint(stat=Stat.SPEED, value=90)]

        result = repository._serialize_hints(hints)

        assert result == [{"type": "stat", "stat": "speed", "value": 90}]

    def test_serializes_comparison_hint(
        self, repository: PostgresGameRepository, pikachu: Pokemon
    ) -> None:
        hints: list[Hint] = [
            ComparisonHint(
                pokemon=pikachu,
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

    def test_serializes_multiple_hints(
        self, repository: PostgresGameRepository, pikachu: Pokemon
    ) -> None:
        hints: list[Hint] = [
            StatHint(stat=Stat.HP, value=35),
            ComparisonHint(
                pokemon=pikachu,
                comparisons={stat: Comparison.EQUAL for stat in Stat},
            ),
        ]

        result = repository._serialize_hints(hints)

        assert len(result) == 2
        assert result[0]["type"] == "stat"
        assert result[1]["type"] == "comparison"
