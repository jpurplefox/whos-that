from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Protocol, runtime_checkable

import psycopg
from psycopg_pool import AsyncConnectionPool


@runtime_checkable
class ConnectionProvider(Protocol):
    def connection(self) -> AbstractAsyncContextManager[psycopg.AsyncConnection]: ...


class PoolConnectionProvider:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[psycopg.AsyncConnection]:
        async with self._pool.connection() as conn:
            yield conn


class DirectConnectionProvider:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[psycopg.AsyncConnection]:
        conn = await psycopg.AsyncConnection.connect(self._database_url)
        try:
            yield conn
        finally:
            await conn.close()
