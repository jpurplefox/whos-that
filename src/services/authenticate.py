import uuid

from auth.google_oauth import GoogleOAuthService
from auth.jwt_service import JWTService
from domain.ports.repositories import UserRepository
from domain.user import User


class AuthenticateResponse:
    def __init__(self, user: User, token: str) -> None:
        self.user = user
        self.token = token


class Authenticate:
    def __init__(
        self,
        google_oauth: GoogleOAuthService,
        jwt_service: JWTService,
        user_repository: UserRepository,
    ) -> None:
        self._google_oauth = google_oauth
        self._jwt_service = jwt_service
        self._user_repository = user_repository

    async def execute(self, code: str) -> AuthenticateResponse:
        # Exchange code for access token
        access_token = await self._google_oauth.exchange_code(code)

        # Get user info from Google
        google_user = await self._google_oauth.get_user_info(access_token)

        # Check if user already exists
        existing_user = await self._user_repository.get_by_google_id(google_user.google_id)

        if existing_user:
            # Update user info
            user = existing_user.model_copy(
                update={
                    "email": google_user.email,
                    "display_name": google_user.name,
                    "avatar_url": google_user.picture,
                }
            )
            user = await self._user_repository.save(user)
        else:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                email=google_user.email,
                google_id=google_user.google_id,
                display_name=google_user.name,
                avatar_url=google_user.picture,
            )
            user = await self._user_repository.save(user)

        # Generate JWT
        token = self._jwt_service.create_token(user.id)

        return AuthenticateResponse(user=user, token=token)
