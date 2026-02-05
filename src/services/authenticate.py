import uuid

from domain.ports.oauth_provider import OAuthProvider
from domain.ports.repositories import UserRepository
from domain.ports.token_service import TokenService
from domain.user import User


class AuthenticateResponse:
    def __init__(self, user: User, token: str) -> None:
        self.user = user
        self.token = token


class Authenticate:
    def __init__(
        self,
        oauth_provider: OAuthProvider,
        token_service: TokenService,
        user_repository: UserRepository,
    ) -> None:
        self._oauth_provider = oauth_provider
        self._token_service = token_service
        self._user_repository = user_repository

    async def execute(self, code: str) -> AuthenticateResponse:
        # Exchange code for access token
        access_token = await self._oauth_provider.exchange_code(code)

        # Get user info from provider
        oauth_user = await self._oauth_provider.get_user_info(access_token)

        provider_type = self._oauth_provider.provider_type

        # Check if user already exists
        existing_user = await self._user_repository.get_by_provider_id(
            oauth_user.provider_id, provider_type
        )

        if existing_user:
            # Update user info
            user = existing_user.model_copy(
                update={
                    "email": oauth_user.email,
                    "display_name": oauth_user.name,
                    "avatar_url": oauth_user.picture,
                }
            )
            user = await self._user_repository.save(user)
        else:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                email=oauth_user.email,
                provider_id=oauth_user.provider_id,
                provider_type=provider_type,
                display_name=oauth_user.name,
                avatar_url=oauth_user.picture,
            )
            user = await self._user_repository.save(user)

        # Generate JWT
        token = self._token_service.create_token(user.id)

        return AuthenticateResponse(user=user, token=token)
