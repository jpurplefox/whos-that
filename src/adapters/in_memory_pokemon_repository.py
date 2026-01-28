from domain.exceptions import PokemonNotFound
from domain.pokemon import Pokemon


class InMemoryPokemonRepository:
    def __init__(self, pokemon_list: list[Pokemon]):
        self._pokemon_by_id: dict[int, Pokemon] = {}
        self._pokemon_by_name: dict[str, Pokemon] = {}
        for pokemon in pokemon_list:
            self._pokemon_by_id[pokemon.id] = pokemon
            self._pokemon_by_name[pokemon.name.lower()] = pokemon

    async def get_by_number(self, number: int) -> Pokemon:
        pokemon = self._pokemon_by_id.get(number)
        if pokemon is None:
            raise PokemonNotFound(f"Pokemon with number {number} not found")
        return pokemon

    async def get_by_name(self, name: str) -> Pokemon:
        pokemon = self._pokemon_by_name.get(name.lower())
        if pokemon is None:
            raise PokemonNotFound(f"Pokemon '{name}' not found")
        return pokemon
