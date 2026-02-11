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
    primary_type: str
    secondary_type: str | None = None
    evolves_from: int | None = None
    evolves_to: list[int] = []
    moves: list[str] = []

    def get_stat(self, stat: Stat) -> int:
        value: int = getattr(self, stat.value)
        return value

    @property
    def is_fully_evolved(self) -> bool:
        return len(self.evolves_to) == 0
