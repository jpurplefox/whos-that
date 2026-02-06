from domain.balance import DifficultyConfig
from domain.difficulty import DifficultyLevel
from domain.game import Game
from domain.hint_factory import HintCreatorRegistry
from domain.ports.random_generator import RandomGenerator
from domain.ports.random_pokemon_selector import RandomPokemonSelector
from domain.ports.repositories import GameRepository


class StartGame:
    def __init__(
        self,
        pokemon_selector: RandomPokemonSelector,
        random_generator: RandomGenerator,
        game_repository: GameRepository,
        difficulty_config: DifficultyConfig,
        hint_registry: HintCreatorRegistry,
    ):
        self.pokemon_selector = pokemon_selector
        self.random_generator = random_generator
        self.game_repository = game_repository
        self.difficulty_config = difficulty_config
        self.hint_registry = hint_registry

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
        
        # Select one random hint set from the available sets
        if difficulty_settings.initial_hints:
            num_hint_sets = len(difficulty_settings.initial_hints)
            selected_index = self.random_generator.randint(0, num_hint_sets - 1)
            selected_hint_set = difficulty_settings.initial_hints[selected_index]
            
            # Create hints from the selected set
            for hint_type_name in selected_hint_set:
                hint = self.hint_registry.create(
                    hint_type_name, pokemon, game.hints, self.random_generator
                )
                game.hints.append(hint)
        
        return await self.game_repository.save(game)
