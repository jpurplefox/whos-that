from typing import Protocol

from domain.ports.random_generator import RandomGenerator
from domain.balance import DifficultyConfig
from domain.difficulty import DifficultyLevel
from domain.game import Game
from domain.hint import FullyEvolvedHint, Hint, PrimaryTypeHint, SecondaryTypeHint, StatHint
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


class FullyEvolvedHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return FullyEvolvedHint.create(pokemon)


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
    registry.register("fully_evolved", FullyEvolvedHintCreator())
    return registry


hint_creator_registry = _create_registry()


class StartGame:
    def __init__(
        self,
        pokemon_selector: RandomPokemonSelector,
        random_generator: RandomGenerator,
        game_repository: GameRepository,
        difficulty_config: DifficultyConfig,
    ):
        self.pokemon_selector = pokemon_selector
        self.random_generator = random_generator
        self.game_repository = game_repository
        self.difficulty_config = difficulty_config

    async def execute(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        user_id: str | None = None,
    ) -> Game:
        difficulty_settings = self.difficulty_config.get(difficulty)
        pokemon = await self.pokemon_selector.select()
        game = Game(
            pokemon=pokemon,
            hint_costs=difficulty_settings.hint_costs,
            max_attempts=difficulty_settings.max_attempts,
            battery=difficulty_settings.initial_battery,
            max_battery=difficulty_settings.max_battery,
            battery_recovery=difficulty_settings.battery_recovery,
            user_id=user_id,
        )
        for hint_type_name in difficulty_settings.initial_hints:
            hint = hint_creator_registry.create(
                hint_type_name, pokemon, game.hints, self.random_generator
            )
            game.hints.append(hint)
        return await self.game_repository.save(game)
