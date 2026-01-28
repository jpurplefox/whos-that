import json
import uuid
from typing import Any, Protocol

import psycopg
from pypika import PostgreSQLQuery, Table

from domain.exceptions import GameNotFound
from domain.game import Comparison, ComparisonHint, Game, Hint, StatHint
from domain.pokemon import Pokemon
from domain.stat import Stat


class PokemonRepository(Protocol):
    async def get_by_number(self, number: int) -> Pokemon: ...


class PostgresGameRepository:
    def __init__(
        self,
        connection: psycopg.AsyncConnection,
        pokemon_repository: PokemonRepository,
    ) -> None:
        self._connection = connection
        self._pokemon_repository = pokemon_repository

    async def save(self, game: Game) -> Game:
        if game.id is None:
            game.id = str(uuid.uuid4())

        games = Table("games")
        hints_json = json.dumps(self._serialize_hints(game.hints))
        attempts_json = json.dumps([p.id for p in game.attempts])

        select_query = (
            PostgreSQLQuery.from_(games).select(games.id).where(games.id == game.id)
        )

        async with self._connection.cursor() as cursor:
            await cursor.execute(str(select_query))
            exists = await cursor.fetchone()

            if exists:
                update_query = (
                    PostgreSQLQuery.update(games)
                    .set(games.pokemon_id, game.pokemon.id)
                    .set(games.max_attempts, game.max_attempts)
                    .set(games.hints, hints_json)
                    .set(games.attempts, attempts_json)
                    .set(games.battery, game.battery)
                    .set(games.max_battery, game.max_battery)
                    .set(games.battery_recovery, game.battery_recovery)
                    .set(games.consulted_this_turn, game.consulted_this_turn)
                    .where(games.id == game.id)
                )
                await cursor.execute(str(update_query))
            else:
                insert_query = PostgreSQLQuery.into(games).columns(
                    "id",
                    "pokemon_id",
                    "max_attempts",
                    "hints",
                    "attempts",
                    "battery",
                    "max_battery",
                    "battery_recovery",
                    "consulted_this_turn",
                ).insert(
                    game.id,
                    game.pokemon.id,
                    game.max_attempts,
                    hints_json,
                    attempts_json,
                    game.battery,
                    game.max_battery,
                    game.battery_recovery,
                    game.consulted_this_turn,
                )
                await cursor.execute(str(insert_query))

            await self._connection.commit()

        return game

    async def get(self, game_id: str) -> Game:
        games = Table("games")
        query = (
            PostgreSQLQuery.from_(games)
            .select(
                games.id,
                games.pokemon_id,
                games.max_attempts,
                games.hints,
                games.attempts,
                games.battery,
                games.max_battery,
                games.battery_recovery,
                games.consulted_this_turn,
            )
            .where(games.id == game_id)
        )

        async with self._connection.cursor() as cursor:
            await cursor.execute(str(query))
            row = await cursor.fetchone()

        if row is None:
            raise GameNotFound(f"Game '{game_id}' not found")

        (
            id_,
            pokemon_id,
            max_attempts,
            hints_json,
            attempts_json,
            battery,
            max_battery,
            battery_recovery,
            consulted_this_turn,
        ) = row

        pokemon = await self._pokemon_repository.get_by_number(pokemon_id)
        hints = await self._deserialize_hints(hints_json)
        attempts = await self._deserialize_attempts(attempts_json)

        return Game(
            id=id_,
            pokemon=pokemon,
            max_attempts=max_attempts,
            hints=hints,
            attempts=attempts,
            battery=battery,
            max_battery=max_battery,
            battery_recovery=battery_recovery,
            consulted_this_turn=consulted_this_turn,
        )

    def _serialize_hints(self, hints: list[Hint]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for hint in hints:
            if isinstance(hint, StatHint):
                result.append(
                    {
                        "type": "stat",
                        "stat": hint.stat.value,
                        "value": hint.value,
                    }
                )
            elif isinstance(hint, ComparisonHint):
                result.append(
                    {
                        "type": "comparison",
                        "pokemon_id": hint.pokemon.id,
                        "comparisons": {
                            stat.value: comparison.value
                            for stat, comparison in hint.comparisons.items()
                        },
                    }
                )
        return result

    async def _deserialize_hints(self, hints_data: list[dict[str, Any]]) -> list[Hint]:
        result: list[Hint] = []
        for hint_data in hints_data:
            if hint_data["type"] == "stat":
                result.append(
                    StatHint(
                        stat=Stat(hint_data["stat"]),
                        value=hint_data["value"],
                    )
                )
            elif hint_data["type"] == "comparison":
                pokemon = await self._pokemon_repository.get_by_number(
                    hint_data["pokemon_id"]
                )
                comparisons = {
                    Stat(stat): Comparison(comparison)
                    for stat, comparison in hint_data["comparisons"].items()
                }
                result.append(
                    ComparisonHint(
                        pokemon=pokemon,
                        comparisons=comparisons,
                    )
                )
        return result

    async def _deserialize_attempts(self, attempts_data: list[int]) -> list[Pokemon]:
        result: list[Pokemon] = []
        for pokemon_id in attempts_data:
            pokemon = await self._pokemon_repository.get_by_number(pokemon_id)
            result.append(pokemon)
        return result
