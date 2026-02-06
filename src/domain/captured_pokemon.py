from datetime import datetime

from pydantic import BaseModel


class CapturedPokemon(BaseModel):
    user_id: str
    pokemon_id: int
    first_caught_at: datetime
    times_caught: int = 1
