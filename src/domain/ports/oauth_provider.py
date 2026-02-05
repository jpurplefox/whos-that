from typing import Protocol

from pydantic import BaseModel


class OAuthUserInfo(BaseModel):
    provider_id: str
    email: str
    name: str | None = None
    picture: str | None = None


class OAuthProvider(Protocol):
    @property
    def provider_type(self) -> str: ...
    async def exchange_code(self, code: str) -> str: ...
    async def get_user_info(self, access_token: str) -> OAuthUserInfo: ...
