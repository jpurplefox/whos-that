from infrastructure.random_generator import RandomGenerator
from domain.pokemon import Pokemon


class InMemoryPokemonRepository:
    def __init__(self, random_generator: RandomGenerator):
        self.random_generator = random_generator
        self.pokemons: dict[int, Pokemon] = {}
        self.pokemons_by_name: dict[str, Pokemon] = {}

    def add(self, pokemon: Pokemon) -> None:
        self.pokemons[pokemon.id] = pokemon
        self.pokemons_by_name[pokemon.name.lower()] = pokemon

    async def get_random_pokemon(self) -> Pokemon:
        pokemon_ids = list(self.pokemons.keys())
        index = self.random_generator.randint(0, len(pokemon_ids) - 1)
        return self.pokemons[pokemon_ids[index]]

    async def get_by_name(self, name: str) -> Pokemon:
        return self.pokemons_by_name[name.lower()]
