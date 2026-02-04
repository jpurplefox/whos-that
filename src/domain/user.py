from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    google_id: str
    display_name: str | None = None
    avatar_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
