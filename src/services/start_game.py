from domain.game import Game
from domain.ports.random_pokemon_selector import RandomPokemonSelector
from domain.ports.random_stat_selector import RandomStatSelector
from domain.ports.repositories import GameRepository


class StartGame:
    def __init__(
        self,
        pokemon_selector: RandomPokemonSelector,
        stat_selector: RandomStatSelector,
        game_repository: GameRepository,
    ):
        self.pokemon_selector = pokemon_selector
        self.stat_selector = stat_selector
        self.game_repository = game_repository

    async def execute(self) -> Game:
        pokemon = await self.pokemon_selector.select()
        game = Game(pokemon=pokemon)
        random_stat = self.stat_selector.select()
        game.add_stat_hint(random_stat)
        return await self.game_repository.save(game)
