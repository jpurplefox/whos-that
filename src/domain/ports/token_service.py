from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime


class TokenService(Protocol):
    def create_token(self, user_id: str) -> str: ...
    def decode_token(self, token: str) -> TokenPayload | None: ...
