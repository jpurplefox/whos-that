from domain.captured_pokemon import CapturedPokemon
from domain.ports.repositories import CollectionRepository


class GetCollection:
    def __init__(self, collection_repository: CollectionRepository):
        self._collection_repository = collection_repository

    async def execute(self, user_id: str) -> list[CapturedPokemon]:
        return await self._collection_repository.get_by_user_id(user_id)
