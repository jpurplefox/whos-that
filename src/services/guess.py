from domain.game import Game
from domain.ports.repositories import GameRepository, PokemonRepository


class Guess:
    def __init__(
        self,
        pokemon_repository: PokemonRepository,
        game_repository: GameRepository,
    ):
        self.pokemon_repository = pokemon_repository
        self.game_repository = game_repository

    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        game = await self.game_repository.get(game_id)
        pokemon = await self.pokemon_repository.get_by_name(pokemon_name)
        game.guess(pokemon)
        return await self.game_repository.save(game)
