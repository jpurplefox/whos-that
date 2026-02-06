from typing import Any

from psycopg.rows import dict_row
from pypika import Parameter, PostgreSQLQuery, Table
from pypika import functions as fn

from adapters.connection_provider import ConnectionProvider
from domain.captured_pokemon import CapturedPokemon
from domain.pokemon import Pokemon
from domain.ports.repositories import PokemonRepository


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
    return str(
        PostgreSQLQuery.into(_user_collection)
        .columns("user_id", "pokemon_id", "first_caught_at", "times_caught")
        .insert(
            Parameter("%(user_id)s"),
            Parameter("%(pokemon_id)s"),
            fn.Now(),  # type: ignore[no-untyped-call]
            1,
        )
        .on_conflict(_user_collection.user_id, _user_collection.pokemon_id)  # type: ignore[operator]
        .do_update(
            _user_collection.times_caught,
            _user_collection.times_caught + 1,
        )
        .returning(
            _user_collection.user_id,
            _user_collection.pokemon_id,
            _user_collection.first_caught_at,
            _user_collection.times_caught,
        )
    )


class PostgresCollectionRepository:
    def __init__(
        self,
        connection_provider: ConnectionProvider,
        pokemon_repository: PokemonRepository,
    ) -> None:
        self._connection_provider = connection_provider
        self._pokemon_repository = pokemon_repository

    async def capture(self, user_id: str, pokemon: Pokemon) -> CapturedPokemon:
        params = {
            "user_id": user_id,
            "pokemon_id": pokemon.id,
        }

        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_upsert_capture(), params)
                row = await cursor.fetchone()
                await conn.commit()

        assert row is not None
        return self._row_to_captured_pokemon(row, pokemon)

    async def get_by_user_id(self, user_id: str) -> list[CapturedPokemon]:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_by_user_id(), {"user_id": user_id})
                rows = await cursor.fetchall()

        result = []
        for row in rows:
            pokemon = await self._pokemon_repository.get_by_number(row["pokemon_id"])
            result.append(self._row_to_captured_pokemon(row, pokemon))
        return result

    def _row_to_captured_pokemon(
        self, row: dict[str, Any], pokemon: Pokemon
    ) -> CapturedPokemon:
        return CapturedPokemon(
            user_id=str(row["user_id"]),
            pokemon=pokemon,
            first_caught_at=row["first_caught_at"],
            times_caught=int(row["times_caught"]),
        )
