from domain.game import Game
from domain.ports.repositories import GameRepository, PokemonRepository
from domain.ports.random_stat_selector import RandomStatSelector


class GameService:
    def __init__(
        self,
        pokemon_repository: PokemonRepository,
        stat_selector: RandomStatSelector,
        game_repository: GameRepository,
    ):
        self.pokemon_repository = pokemon_repository
        self.stat_selector = stat_selector
        self.game_repository = game_repository

    async def start_game(self) -> Game:
        pokemon = await self.pokemon_repository.get_random_pokemon()
        game = Game(pokemon=pokemon)
        random_stat = self.stat_selector.select()
        game.add_stat_hint(random_stat)
        return await self.game_repository.save(game)

    async def guess(self, game_id: str, pokemon_name: str) -> Game:
        game = await self.game_repository.get(game_id)
        pokemon = await self.pokemon_repository.get_by_name(pokemon_name)
        game.guess(pokemon)
        return await self.game_repository.save(game)
