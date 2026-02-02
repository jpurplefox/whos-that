from domain.balance import Balance
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
        balance: Balance,
    ):
        self.pokemon_selector = pokemon_selector
        self.stat_selector = stat_selector
        self.game_repository = game_repository
        self.balance = balance

    async def execute(self) -> Game:
        pokemon = await self.pokemon_selector.select()
        game = Game(
            pokemon=pokemon,
            hint_costs=self.balance.hint_costs,
            max_attempts=self.balance.max_attempts,
            battery=self.balance.initial_battery,
            max_battery=self.balance.max_battery,
            battery_recovery=self.balance.battery_recovery,
        )
        random_stat = self.stat_selector.select()
        hint = StatHint.create(pokemon, random_stat)
        game.hints.append(hint)
        return await self.game_repository.save(game)
