from domain.captured_pokemon import CapturedPokemon
from domain.pokemon import Pokemon
from domain.ports.repositories import CollectionRepository


class CapturePokemon:
    def __init__(self, collection_repository: CollectionRepository):
        self._collection_repository = collection_repository

    async def execute(self, user_id: str, pokemon: Pokemon) -> CapturedPokemon:
        return await self._collection_repository.capture(user_id, pokemon)
