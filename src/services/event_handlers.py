from domain.events import DomainEvent, EventHandler, GameWon
from services.capture_pokemon import CapturePokemon


def create_capture_pokemon_handler(capture_pokemon: CapturePokemon) -> EventHandler:
    """Creates a handler that captures pokemon when a game is won by an authenticated user."""

    async def handle(event: DomainEvent) -> None:
        if not isinstance(event, GameWon):
            return
        game = event.game
        if game.user_id is None:
            return
        await capture_pokemon.execute(game.user_id, game.pokemon)

    return handle
