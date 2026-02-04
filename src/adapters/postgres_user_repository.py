import uuid
from datetime import datetime, timezone
from typing import Any

from psycopg.rows import dict_row
from pypika import Parameter, PostgreSQLQuery, Table

from adapters.connection_provider import ConnectionProvider
from domain.user import User


_users = Table("users")


def _select_user_by_id() -> str:
    return str(
        PostgreSQLQuery.from_(_users)
        .select(
            _users.id,
            _users.email,
            _users.google_id,
            _users.display_name,
            _users.avatar_url,
            _users.created_at,
            _users.updated_at,
        )
        .where(_users.id == Parameter("%(id)s"))
    )


def _select_user_by_google_id() -> str:
    return str(
        PostgreSQLQuery.from_(_users)
        .select(
            _users.id,
            _users.email,
            _users.google_id,
            _users.display_name,
            _users.avatar_url,
            _users.created_at,
            _users.updated_at,
        )
        .where(_users.google_id == Parameter("%(google_id)s"))
    )


def _select_user_by_email() -> str:
    return str(
        PostgreSQLQuery.from_(_users)
        .select(
            _users.id,
            _users.email,
            _users.google_id,
            _users.display_name,
            _users.avatar_url,
            _users.created_at,
            _users.updated_at,
        )
        .where(_users.email == Parameter("%(email)s"))
    )


def _upsert_user() -> str:
    return str(
        PostgreSQLQuery.into(_users)
        .columns(
            "id",
            "email",
            "google_id",
            "display_name",
            "avatar_url",
            "created_at",
            "updated_at",
        )
        .insert(
            Parameter("%(id)s"),
            Parameter("%(email)s"),
            Parameter("%(google_id)s"),
            Parameter("%(display_name)s"),
            Parameter("%(avatar_url)s"),
            Parameter("%(created_at)s"),
            Parameter("%(updated_at)s"),
        )
        .on_conflict(_users.id)  # type: ignore[operator]
        .do_update(_users.email, Parameter("%(email)s"))
        .do_update(_users.display_name, Parameter("%(display_name)s"))
        .do_update(_users.avatar_url, Parameter("%(avatar_url)s"))
        .do_update(_users.updated_at, Parameter("%(updated_at)s"))
    )


class PostgresUserRepository:
    def __init__(self, connection_provider: ConnectionProvider) -> None:
        self._connection_provider = connection_provider

    async def save(self, user: User) -> User:
        now = datetime.now(timezone.utc)
        user_id = user.id if user.id else str(uuid.uuid4())

        params = {
            "id": user_id,
            "email": user.email,
            "google_id": user.google_id,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at or now,
            "updated_at": now,
        }

        async with self._connection_provider.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(_upsert_user(), params)
                await conn.commit()

        return user.model_copy(
            update={
                "id": user_id,
                "created_at": params["created_at"],
                "updated_at": params["updated_at"],
            }
        )

    async def get_by_id(self, user_id: str) -> User | None:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_user_by_id(), {"id": user_id})
                row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    async def get_by_google_id(self, google_id: str) -> User | None:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_user_by_google_id(), {"google_id": google_id})
                row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    async def get_by_email(self, email: str) -> User | None:
        async with self._connection_provider.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(_select_user_by_email(), {"email": email})
                row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def _row_to_user(self, row: dict[str, Any]) -> User:
        return User(
            id=str(row["id"]),
            email=str(row["email"]),
            google_id=str(row["google_id"]),
            display_name=row["display_name"] if row["display_name"] is None else str(row["display_name"]),
            avatar_url=row["avatar_url"] if row["avatar_url"] is None else str(row["avatar_url"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
