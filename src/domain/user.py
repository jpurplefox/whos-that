from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    provider_id: str
    provider_type: str
    display_name: str | None = None
    avatar_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
