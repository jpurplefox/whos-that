from pydantic import BaseModel

from domain.stat import Stat


class Pokemon(BaseModel):
    id: int
    name: str
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    image_url: str

    def get_stat(self, stat: Stat) -> int:
        value: int = getattr(self, stat.value)
        return value
