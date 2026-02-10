import secrets
from urllib.parse import urlencode

import httpx

from domain.ports.oauth_provider import OAuthUserInfo


class GoogleOAuthService:
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._pending_states: set[str] = set()

    @property
    def provider_type(self) -> str:
        return "google"

    def get_authorization_url(self) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        self._pending_states.add(state)
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "state": state,
        }
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}", state

    def consume_state(self, state: str) -> bool:
        if state in self._pending_states:
            self._pending_states.discard(state)
            return True
        return False

    async def exchange_code(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self._redirect_uri,
                },
            )
            response.raise_for_status()
            data = response.json()
            access_token: str = data["access_token"]
            return access_token

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return OAuthUserInfo(
                provider_id=data["id"],
                email=data["email"],
                name=data.get("name"),
                picture=data.get("picture"),
            )
