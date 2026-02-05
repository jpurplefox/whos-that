from domain.exceptions import InvalidToken
from domain.ports.repositories import UserRepository
from domain.ports.token_service import TokenService
from domain.user import User


class ResolveUser:
    def __init__(
        self,
        token_service: TokenService,
        user_repository: UserRepository,
    ) -> None:
        self._token_service = token_service
        self._user_repository = user_repository

    async def execute(self, token: str) -> User:
        payload = self._token_service.decode_token(token)
        if payload is None:
            raise InvalidToken()
        return await self._user_repository.get_by_id(payload.sub)
