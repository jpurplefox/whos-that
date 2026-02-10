from adapters.connection_provider import ConnectionProvider


class PostgresOAuthStateStore:
    def __init__(self, connection_provider: ConnectionProvider, ttl_seconds: int = 600) -> None:
        self._connection_provider = connection_provider
        self._ttl_seconds = ttl_seconds

    async def save(self, state: str) -> None:
        async with self._connection_provider.connection() as conn:
            await conn.execute(
                "INSERT INTO oauth_states (state) VALUES (%(state)s)",
                {"state": state},
            )
            await conn.commit()

    async def consume(self, state: str) -> bool:
        async with self._connection_provider.connection() as conn:
            result = await conn.execute(
                """
                DELETE FROM oauth_states
                WHERE state = %(state)s
                  AND created_at > NOW() - INTERVAL '1 second' * %(ttl)s
                RETURNING state
                """,
                {"state": state, "ttl": self._ttl_seconds},
            )
            row = await result.fetchone()
            await conn.commit()
            return row is not None
