from domain.pokemon import Pokemon
from domain.ports.repositories import PokemonRepository
from infrastructure.random_generator import RandomGenerator


class RandomPokemonSelector:
    MAX_POKEMON_NUMBER = 151

    def __init__(
        self,
        pokemon_repository: PokemonRepository,
        random_generator: RandomGenerator,
    ):
        self.pokemon_repository = pokemon_repository
        self.random_generator = random_generator

    async def select(self) -> Pokemon:
        pokemon_number = self.random_generator.randint(1, self.MAX_POKEMON_NUMBER)
        return await self.pokemon_repository.get_by_number(pokemon_number)
