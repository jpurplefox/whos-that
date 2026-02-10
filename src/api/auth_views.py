from litestar import Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from pydantic import BaseModel

from api.dependencies import get_authenticate, get_google_oauth
from auth.google_oauth import GoogleOAuthService
from services.authenticate import Authenticate


class GoogleAuthUrlResponse(BaseModel):
    url: str
    state: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    display_name: str | None
    avatar_url: str | None


@get("/auth/google/url")
async def get_google_auth_url(
    google_oauth: GoogleOAuthService = Dependency(skip_validation=True),
) -> GoogleAuthUrlResponse:
    url, state = google_oauth.get_authorization_url()
    return GoogleAuthUrlResponse(url=url, state=state)


@post("/auth/google/callback")
async def google_callback(
    data: GoogleCallbackRequest,
    google_oauth: GoogleOAuthService = Dependency(skip_validation=True),
    authenticate: Authenticate = Dependency(skip_validation=True),
) -> AuthResponse:
    if not google_oauth.consume_state(data.state):
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    result = await authenticate.execute(data.code)
    return AuthResponse(
        token=result.token,
        user_id=result.user.id,
        email=result.user.email,
        display_name=result.user.display_name,
        avatar_url=result.user.avatar_url,
    )


auth_router = Router(
    path="/",
    route_handlers=[get_google_auth_url, google_callback],
    dependencies={
        "google_oauth": Provide(get_google_oauth),
        "authenticate": Provide(get_authenticate),
    },
)
