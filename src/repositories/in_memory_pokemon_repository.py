from domain.pokemon import Pokemon


class InMemoryPokemonRepository:
    def __init__(self) -> None:
        self.pokemons: dict[int, Pokemon] = {}
        self.pokemons_by_name: dict[str, Pokemon] = {}

    def add(self, pokemon: Pokemon) -> None:
        self.pokemons[pokemon.id] = pokemon
        self.pokemons_by_name[pokemon.name.lower()] = pokemon

    async def get_by_number(self, number: int) -> Pokemon:
        return self.pokemons[number]

    async def get_by_name(self, name: str) -> Pokemon:
        return self.pokemons_by_name[name.lower()]
