import uuid
from copy import deepcopy
from datetime import datetime, timezone

from domain.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self._by_google_id: dict[str, str] = {}
        self._by_email: dict[str, str] = {}

    async def save(self, user: User) -> User:
        now = datetime.now(timezone.utc)
        user_id = user.id if user.id else str(uuid.uuid4())

        saved_user = user.model_copy(
            update={
                "id": user_id,
                "created_at": user.created_at or now,
                "updated_at": now,
            }
        )

        self.users[user_id] = deepcopy(saved_user)
        self._by_google_id[saved_user.google_id] = user_id
        self._by_email[saved_user.email] = user_id

        return saved_user

    async def get_by_id(self, user_id: str) -> User | None:
        user = self.users.get(user_id)
        return deepcopy(user) if user else None

    async def get_by_google_id(self, google_id: str) -> User | None:
        user_id = self._by_google_id.get(google_id)
        if user_id is None:
            return None
        return await self.get_by_id(user_id)

    async def get_by_email(self, email: str) -> User | None:
        user_id = self._by_email.get(email)
        if user_id is None:
            return None
        return await self.get_by_id(user_id)
