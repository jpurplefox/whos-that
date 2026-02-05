import uuid
from copy import deepcopy
from datetime import datetime, timezone

from domain.exceptions import UserNotFound
from domain.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self._by_provider: dict[tuple[str, str], str] = {}

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
        self._by_provider[(saved_user.provider_id, saved_user.provider_type)] = user_id

        return saved_user

    async def get_by_id(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFound(f"User '{user_id}' not found")
        return deepcopy(user)

    async def get_by_provider_id(self, provider_id: str, provider_type: str) -> User | None:
        user_id = self._by_provider.get((provider_id, provider_type))
        if user_id is None:
            return None
        return deepcopy(self.users[user_id])
