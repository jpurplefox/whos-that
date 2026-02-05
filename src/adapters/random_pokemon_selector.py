from domain.pokemon import Pokemon
from domain.ports.repositories import PokemonRepository
from domain.ports.random_generator import RandomGenerator


class RandomPokemonSelector:
    def __init__(
        self,
        pokemon_repository: PokemonRepository,
        random_generator: RandomGenerator,
        max_pokemon_number: int,
    ):
        self.pokemon_repository = pokemon_repository
        self.random_generator = random_generator
        self.max_pokemon_number = max_pokemon_number

    async def select(self) -> Pokemon:
        pokemon_number = self.random_generator.randint(1, self.max_pokemon_number)
        return await self.pokemon_repository.get_by_number(pokemon_number)
