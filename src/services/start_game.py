from domain.game import Game, StatHint
from domain.ports.random_pokemon_selector import RandomPokemonSelector
from domain.ports.random_stat_selector import RandomStatSelector
from domain.ports.repositories import GameRepository


class StartGame:
    def __init__(
        self,
        pokemon_selector: RandomPokemonSelector,
        stat_selector: RandomStatSelector,
        game_repository: GameRepository,
        max_attempts: int,
        max_battery: int = 100,
        battery_recovery: int = 10,
    ):
        self.pokemon_selector = pokemon_selector
        self.stat_selector = stat_selector
        self.game_repository = game_repository
        self.max_attempts = max_attempts
        self.max_battery = max_battery
        self.battery_recovery = battery_recovery

    async def execute(self) -> Game:
        pokemon = await self.pokemon_selector.select()
        game = Game(
            pokemon=pokemon,
            max_attempts=self.max_attempts,
            battery=self.max_battery,
            max_battery=self.max_battery,
            battery_recovery=self.battery_recovery,
        )
        random_stat = self.stat_selector.select()
        hint = StatHint.create(pokemon, random_stat)
        game.hints.append(hint)
        return await self.game_repository.save(game)
