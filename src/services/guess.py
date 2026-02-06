from domain.events import EventBus, GameWon
from domain.exceptions import GameAccessDenied
from domain.game import Game
from domain.ports.repositories import GameRepository, PokemonRepository


class Guess:
    def __init__(
        self,
        pokemon_repository: PokemonRepository,
        game_repository: GameRepository,
        event_bus: EventBus,
    ):
        self.pokemon_repository = pokemon_repository
        self.game_repository = game_repository
        self._event_bus = event_bus

    async def execute(
        self, game_id: str, pokemon_name: str, user_id: str | None = None
    ) -> Game:
        game = await self.game_repository.get(game_id)
        if game.user_id is not None and user_id != game.user_id:
            raise GameAccessDenied()
        pokemon = await self.pokemon_repository.get_by_name(pokemon_name)
        is_correct = game.guess(pokemon)
        saved_game = await self.game_repository.save(game)

        if is_correct:
            await self._event_bus.publish(GameWon(game=saved_game))

        return saved_game
