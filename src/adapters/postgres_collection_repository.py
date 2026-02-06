from typing import Any

from psycopg.rows import dict_row
from pypika import Parameter, PostgreSQLQuery, Table

from adapters.connection_provider import ConnectionProvider
from domain.captured_pokemon import CapturedPokemon


_user_collection = Table("user_collection")


def _select_by_user_id() -> str:
    return str(
        PostgreSQLQuery.from_(_user_collection)
        .select(
            _user_collection.user_id,
            _user_collection.pokemon_id,
            _user_collection.first_caught_at,
            _user_collection.times_caught,
        )
        .where(_user_collection.user_id == Parameter("%(user_id)s"))
    )


def _upsert_capture() -> str:
    return """
        INSERT INTO user_collection (user_id, pokemon_id, first_caught_at, times_caught)
        VALUES (%(user_id)s, %(pokemon_id)s, NOW(), 1)
        ON CONFLICT (user_id, pokemon_id)
        DO UPDATE SET times_caught = user_collection.times_caught + 1
        RETURNING user_id, pokemon_id, first_caught_at, times_caught
    """


class PostgresCollectionRepository:
    def __init__(self, connection_provider: ConnectionProvider) -> None:
        self._connection_provider = connection_provider

    async def capture(self, user_id: str, pokemon_id: int) -> CapturedPokemon:
        params = {
            "user_id": user_id,
            "pokemon_id": pokemon_id,
        }

        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_upsert_capture(), params)
                row = await cursor.fetchone()
                await conn.commit()

        assert row is not None
        return self._row_to_captured_pokemon(row)

    async def get_by_user_id(self, user_id: str) -> list[CapturedPokemon]:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_by_user_id(), {"user_id": user_id})
                rows = await cursor.fetchall()

        return [self._row_to_captured_pokemon(row) for row in rows]

    def _row_to_captured_pokemon(self, row: dict[str, Any]) -> CapturedPokemon:
        return CapturedPokemon(
            user_id=str(row["user_id"]),
            pokemon_id=int(row["pokemon_id"]),
            first_caught_at=row["first_caught_at"],
            times_caught=int(row["times_caught"]),
        )
