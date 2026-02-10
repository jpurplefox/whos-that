import json
import uuid
from datetime import datetime, timezone
from typing import Any

from psycopg.rows import dict_row
from pypika import Order, Parameter, PostgreSQLQuery, Table

from adapters.connection_provider import ConnectionProvider
from adapters.hint_serializers import HintSerializerRegistry
from domain.balance import HintCosts
from domain.exceptions import GameNotFound
from domain.game import Game
from domain.hint import Hint
from domain.pokemon import Pokemon
from domain.ports.repositories import PokemonRepository


_games = Table("games")


def _select_game_by_id() -> str:
    return str(
        PostgreSQLQuery.from_(_games)
        .select(
            _games.id,
            _games.pokemon_id,
            _games.hint_costs,
            _games.max_attempts,
            _games.hints,
            _games.attempts,
            _games.battery,
            _games.max_battery,
            _games.battery_recovery,
            _games.consulted_this_turn,
            _games.user_id,
            _games.created_at,
            _games.initial_battery,
            _games.difficulty_multiplier,
        )
        .where(_games.id == Parameter("%(id)s"))
    )


def _select_games_by_user_id() -> str:
    return str(
        PostgreSQLQuery.from_(_games)
        .select(
            _games.id,
            _games.pokemon_id,
            _games.hint_costs,
            _games.max_attempts,
            _games.hints,
            _games.attempts,
            _games.battery,
            _games.max_battery,
            _games.battery_recovery,
            _games.consulted_this_turn,
            _games.user_id,
            _games.created_at,
            _games.initial_battery,
            _games.difficulty_multiplier,
        )
        .where(_games.user_id == Parameter("%(user_id)s"))
        .orderby(_games.created_at, order=Order.desc)
    )


def _upsert_game() -> str:
    return str(
        PostgreSQLQuery.into(_games)
        .columns(
            "id",
            "pokemon_id",
            "hint_costs",
            "max_attempts",
            "hints",
            "attempts",
            "battery",
            "max_battery",
            "battery_recovery",
            "consulted_this_turn",
            "user_id",
            "initial_battery",
            "difficulty_multiplier",
        )
        .insert(
            Parameter("%(id)s"),
            Parameter("%(pokemon_id)s"),
            Parameter("%(hint_costs)s"),
            Parameter("%(max_attempts)s"),
            Parameter("%(hints)s"),
            Parameter("%(attempts)s"),
            Parameter("%(battery)s"),
            Parameter("%(max_battery)s"),
            Parameter("%(battery_recovery)s"),
            Parameter("%(consulted_this_turn)s"),
            Parameter("%(user_id)s"),
            Parameter("%(initial_battery)s"),
            Parameter("%(difficulty_multiplier)s"),
        )
        .on_conflict(_games.id)  # type: ignore[operator]
        .do_update(_games.pokemon_id, Parameter("%(pokemon_id)s"))
        .do_update(_games.hint_costs, Parameter("%(hint_costs)s"))
        .do_update(_games.max_attempts, Parameter("%(max_attempts)s"))
        .do_update(_games.hints, Parameter("%(hints)s"))
        .do_update(_games.attempts, Parameter("%(attempts)s"))
        .do_update(_games.battery, Parameter("%(battery)s"))
        .do_update(_games.max_battery, Parameter("%(max_battery)s"))
        .do_update(_games.battery_recovery, Parameter("%(battery_recovery)s"))
        .do_update(_games.consulted_this_turn, Parameter("%(consulted_this_turn)s"))
        .do_update(_games.user_id, Parameter("%(user_id)s"))
        .do_update(_games.initial_battery, Parameter("%(initial_battery)s"))
        .do_update(_games.difficulty_multiplier, Parameter("%(difficulty_multiplier)s"))
    )


class PostgresGameRepository:
    def __init__(
        self,
        connection_provider: ConnectionProvider,
        pokemon_repository: PokemonRepository,
        hint_serializer: HintSerializerRegistry,
    ) -> None:
        self._connection_provider = connection_provider
        self._pokemon_repository = pokemon_repository
        self._hint_serializer = hint_serializer

    async def save(self, game: Game) -> Game:
        is_new = game.id is None
        game_id = game.id if not is_new else str(uuid.uuid4())

        params = {
            "id": game_id,
            "pokemon_id": game.pokemon.id,
            "hint_costs": json.dumps(game.hint_costs.model_dump()),
            "max_attempts": game.max_attempts,
            "hints": json.dumps(self._serialize_hints(game.hints)),
            "attempts": json.dumps([p.id for p in game.attempts]),
            "battery": game.battery,
            "max_battery": game.max_battery,
            "battery_recovery": game.battery_recovery,
            "consulted_this_turn": game.consulted_this_turn,
            "user_id": game.user_id,
            "initial_battery": game.initial_battery,
            "difficulty_multiplier": game.difficulty_multiplier,
        }

        async with self._connection_provider.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(_upsert_game(), params)
                await conn.commit()

        update: dict[str, Any] = {"id": game_id}
        if is_new:
            update["created_at"] = datetime.now(timezone.utc)
        return game.model_copy(update=update)

    async def get(self, game_id: str) -> Game:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_game_by_id(), {"id": game_id})
                row = await cursor.fetchone()

        if row is None:
            raise GameNotFound(f"Game '{game_id}' not found")

        return await self._row_to_game(row)

    async def get_by_user_id(self, user_id: str) -> list[Game]:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_games_by_user_id(), {"user_id": user_id})
                rows = await cursor.fetchall()

        return [await self._row_to_game(row) for row in rows]

    async def _row_to_game(self, row: dict[str, Any]) -> Game:
        pokemon = await self._pokemon_repository.get_by_number(row["pokemon_id"])
        hint_costs = (
            HintCosts.model_validate(row["hint_costs"])
            if row["hint_costs"]
            else HintCosts()
        )
        hints = await self._deserialize_hints(row["hints"])
        attempts = await self._deserialize_attempts(row["attempts"])

        return Game(
            id=row["id"],
            pokemon=pokemon,
            hint_costs=hint_costs,
            max_attempts=row["max_attempts"],
            hints=hints,
            attempts=attempts,
            battery=row["battery"],
            max_battery=row["max_battery"],
            battery_recovery=row["battery_recovery"],
            consulted_this_turn=row["consulted_this_turn"],
            user_id=row.get("user_id"),
            created_at=row.get("created_at"),
            initial_battery=row["initial_battery"] if row.get("initial_battery") is not None else 100,
            difficulty_multiplier=row["difficulty_multiplier"] if row.get("difficulty_multiplier") is not None else 1.0,
        )

    def _serialize_hints(self, hints: list[Hint]) -> list[dict[str, Any]]:
        return [self._hint_serializer.serialize(hint) for hint in hints]

    async def _deserialize_hints(self, hints_data: list[dict[str, Any]]) -> list[Hint]:
        return [await self._hint_serializer.deserialize(hint_data) for hint_data in hints_data]

    async def _deserialize_attempts(self, attempts_data: list[int]) -> list[Pokemon]:
        return [await self._pokemon_repository.get_by_number(pid) for pid in attempts_data]
