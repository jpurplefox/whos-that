from pypika import Parameter, PostgreSQLQuery, Table
from pypika.terms import LiteralValue

from adapters.connection_provider import ConnectionProvider

_oauth_states = Table("oauth_states")


def _insert_state() -> str:
    return str(
        PostgreSQLQuery.into(_oauth_states)
        .columns("state")
        .insert(Parameter("%(state)s"))
    )


def _delete_valid_state() -> str:
    return str(
        PostgreSQLQuery.from_(_oauth_states)
        .where(_oauth_states.state == Parameter("%(state)s"))
        .where(
            _oauth_states.created_at
            > LiteralValue("NOW() - INTERVAL '1 second' * %(ttl)s")
        )
        .delete()
        .returning(_oauth_states.state)
    )


class PostgresOAuthStateStore:
    def __init__(self, connection_provider: ConnectionProvider, ttl_seconds: int = 600) -> None:
        self._connection_provider = connection_provider
        self._ttl_seconds = ttl_seconds

    async def save(self, state: str) -> None:
        async with self._connection_provider.connection() as conn:
            await conn.execute(_insert_state(), {"state": state})
            await conn.commit()

    async def consume(self, state: str) -> bool:
        async with self._connection_provider.connection() as conn:
            result = await conn.execute(
                _delete_valid_state(),
                {"state": state, "ttl": self._ttl_seconds},
            )
            row = await result.fetchone()
            await conn.commit()
            return row is not None
