from datetime import datetime, timedelta, timezone

import jwt
from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime
    iat: datetime


class JWTService:
    def __init__(self, secret: str, algorithm: str, expiration_hours: int) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._expiration_hours = expiration_hours

    def create_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "exp": now + timedelta(hours=self._expiration_hours),
            "iat": now,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> TokenPayload | None:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return TokenPayload(
                sub=payload["sub"],
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
