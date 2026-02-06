from copy import deepcopy
from datetime import datetime, timezone

from domain.captured_pokemon import CapturedPokemon
from domain.pokemon import Pokemon


class InMemoryCollectionRepository:
    def __init__(self) -> None:
        self.collection: dict[tuple[str, int], CapturedPokemon] = {}

    async def capture(self, user_id: str, pokemon: Pokemon) -> CapturedPokemon:
        key = (user_id, pokemon.id)
        now = datetime.now(timezone.utc)

        if key in self.collection:
            existing = self.collection[key]
            updated = existing.model_copy(
                update={"times_caught": existing.times_caught + 1}
            )
            self.collection[key] = updated
            return deepcopy(updated)

        captured = CapturedPokemon(
            user_id=user_id,
            pokemon=pokemon,
            first_caught_at=now,
            times_caught=1,
        )
        self.collection[key] = captured
        return deepcopy(captured)

    async def get_by_user_id(self, user_id: str) -> list[CapturedPokemon]:
        return [
            deepcopy(captured)
            for captured in self.collection.values()
            if captured.user_id == user_id
        ]
