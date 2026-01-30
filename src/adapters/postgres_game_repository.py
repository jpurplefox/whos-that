import json
import uuid
from typing import Any

import psycopg
from psycopg.rows import dict_row
from pypika import Parameter, PostgreSQLQuery, Table

from domain.exceptions import GameNotFound
from domain.game import ComparisonHint, Game, Hint, StatHint
from domain.pokemon import Pokemon
from domain.ports.repositories import PokemonRepository


_games = Table("games")


def _select_game_by_id() -> str:
    return str(
        PostgreSQLQuery.from_(_games)
        .select(
            _games.id,
            _games.pokemon_id,
            _games.max_attempts,
            _games.hints,
            _games.attempts,
            _games.battery,
            _games.max_battery,
            _games.battery_recovery,
            _games.consulted_this_turn,
        )
        .where(_games.id == Parameter("%(id)s"))
    )


def _upsert_game() -> str:
    return str(
        PostgreSQLQuery.into(_games)
        .columns(
            "id",
            "pokemon_id",
            "max_attempts",
            "hints",
            "attempts",
            "battery",
            "max_battery",
            "battery_recovery",
            "consulted_this_turn",
        )
        .insert(
            Parameter("%(id)s"),
            Parameter("%(pokemon_id)s"),
            Parameter("%(max_attempts)s"),
            Parameter("%(hints)s"),
            Parameter("%(attempts)s"),
            Parameter("%(battery)s"),
            Parameter("%(max_battery)s"),
            Parameter("%(battery_recovery)s"),
            Parameter("%(consulted_this_turn)s"),
        )
        .on_conflict(_games.id)  # type: ignore[operator]
        .do_update(_games.pokemon_id, Parameter("%(pokemon_id)s"))
        .do_update(_games.max_attempts, Parameter("%(max_attempts)s"))
        .do_update(_games.hints, Parameter("%(hints)s"))
        .do_update(_games.attempts, Parameter("%(attempts)s"))
        .do_update(_games.battery, Parameter("%(battery)s"))
        .do_update(_games.max_battery, Parameter("%(max_battery)s"))
        .do_update(_games.battery_recovery, Parameter("%(battery_recovery)s"))
        .do_update(_games.consulted_this_turn, Parameter("%(consulted_this_turn)s"))
    )


class PostgresGameRepository:
    def __init__(
        self,
        connection: psycopg.AsyncConnection,
        pokemon_repository: PokemonRepository,
    ) -> None:
        self._connection = connection
        self._pokemon_repository = pokemon_repository

    async def save(self, game: Game) -> Game:
        game_id = game.id if game.id is not None else str(uuid.uuid4())

        params = {
            "id": game_id,
            "pokemon_id": game.pokemon.id,
            "max_attempts": game.max_attempts,
            "hints": json.dumps(self._serialize_hints(game.hints)),
            "attempts": json.dumps([p.id for p in game.attempts]),
            "battery": game.battery,
            "max_battery": game.max_battery,
            "battery_recovery": game.battery_recovery,
            "consulted_this_turn": game.consulted_this_turn,
        }

        async with self._connection.cursor() as cursor:
            await cursor.execute(_upsert_game(), params)
            await self._connection.commit()

        return game.model_copy(update={"id": game_id})

    async def get(self, game_id: str) -> Game:
        async with self._connection.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(_select_game_by_id(), {"id": game_id})
            row = await cursor.fetchone()

        if row is None:
            raise GameNotFound(f"Game '{game_id}' not found")

        pokemon = await self._pokemon_repository.get_by_number(row["pokemon_id"])
        hints = await self._deserialize_hints(row["hints"])
        attempts = await self._deserialize_attempts(row["attempts"])

        return Game(
            id=row["id"],
            pokemon=pokemon,
            max_attempts=row["max_attempts"],
            hints=hints,
            attempts=attempts,
            battery=row["battery"],
            max_battery=row["max_battery"],
            battery_recovery=row["battery_recovery"],
            consulted_this_turn=row["consulted_this_turn"],
        )

    def _serialize_hints(self, hints: list[Hint]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for hint in hints:
            if isinstance(hint, StatHint):
                data = hint.model_dump(mode="json")
                data["type"] = "stat"
                result.append(data)
            elif isinstance(hint, ComparisonHint):
                data = hint.model_dump(mode="json")
                data["type"] = "comparison"
                data["pokemon_id"] = data.pop("pokemon")["id"]
                result.append(data)
        return result

    async def _deserialize_hints(self, hints_data: list[dict[str, Any]]) -> list[Hint]:
        result: list[Hint] = []
        for hint_data in hints_data:
            if hint_data["type"] == "stat":
                result.append(StatHint.model_validate(hint_data))
            elif hint_data["type"] == "comparison":
                pokemon = await self._pokemon_repository.get_by_number(hint_data["pokemon_id"])
                hint_data["pokemon"] = pokemon
                result.append(ComparisonHint.model_validate(hint_data))
        return result

    async def _deserialize_attempts(self, attempts_data: list[int]) -> list[Pokemon]:
        return [await self._pokemon_repository.get_by_number(pid) for pid in attempts_data]
