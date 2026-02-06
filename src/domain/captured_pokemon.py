from datetime import datetime

from pydantic import BaseModel

from domain.pokemon import Pokemon


class CapturedPokemon(BaseModel):
    user_id: str
    pokemon: Pokemon
    first_caught_at: datetime
    times_caught: int = 1
