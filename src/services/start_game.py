from typing import Protocol

from adapters.random_generator import RandomGenerator
from domain.balance import Balance
from domain.game import Game
from domain.hint import Hint, PrimaryTypeHint, SecondaryTypeHint, StatHint
from domain.pokemon import Pokemon
from domain.ports.random_pokemon_selector import RandomPokemonSelector
from domain.ports.repositories import GameRepository


class HintCreator(Protocol):
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint: ...


class StatHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        available = StatHint.available_stats(hints)
        index = random_generator.randint(0, len(available) - 1)
        return StatHint.create(pokemon, available[index])


class PrimaryTypeHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return PrimaryTypeHint.create(pokemon)


class SecondaryTypeHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return SecondaryTypeHint.create(pokemon)


class HintCreatorRegistry:
    def __init__(self) -> None:
        self._creators: dict[str, HintCreator] = {}

    def register(self, type_name: str, creator: HintCreator) -> None:
        self._creators[type_name] = creator

    def create(
        self,
        type_name: str,
        pokemon: Pokemon,
        hints: list[Hint],
        random_generator: RandomGenerator,
    ) -> Hint:
        creator = self._creators.get(type_name)
        if creator is None:
            raise ValueError(f"No creator registered for type '{type_name}'")
        return creator.create(pokemon, hints, random_generator)


def _create_registry() -> HintCreatorRegistry:
    registry = HintCreatorRegistry()
    registry.register("stat", StatHintCreator())
    registry.register("primary_type", PrimaryTypeHintCreator())
    registry.register("secondary_type", SecondaryTypeHintCreator())
    return registry


hint_creator_registry = _create_registry()


class StartGame:
    def __init__(
        self,
        pokemon_selector: RandomPokemonSelector,
        random_generator: RandomGenerator,
        game_repository: GameRepository,
        balance: Balance,
    ):
        self.pokemon_selector = pokemon_selector
        self.random_generator = random_generator
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
        for hint_type_name in self.balance.initial_hints:
            hint = hint_creator_registry.create(
                hint_type_name, pokemon, game.hints, self.random_generator
            )
            game.hints.append(hint)
        return await self.game_repository.save(game)
