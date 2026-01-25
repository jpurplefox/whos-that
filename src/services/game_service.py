from typing import Protocol

from domain.game import Game
from domain.pokemon import Pokemon
from domain.stat import Stat


class PokemonRepository(Protocol):
    def get_random_pokemon(self) -> Pokemon:
        ...

    def get_by_name(self, name: str) -> Pokemon:
        ...


class RandomStatSelector(Protocol):
    def select(self) -> Stat:
        ...


class GameRepository(Protocol):
    def save(self, game: Game) -> Game:
        ...

    def get(self, game_id: str) -> Game:
        ...


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

    def start_game(self) -> Game:
        pokemon = self.pokemon_repository.get_random_pokemon()
        game = Game(pokemon=pokemon)
        random_stat = self.stat_selector.select()
        game.add_stat_hint(random_stat)
        return self.game_repository.save(game)

    def guess(self, game_id: str, pokemon_name: str) -> Game:
        game = self.game_repository.get(game_id)
        pokemon = self.pokemon_repository.get_by_name(pokemon_name)
        game.guess(pokemon)
        return self.game_repository.save(game)
