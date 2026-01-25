from typing import Protocol

from domain.game import Game
from domain.pokemon import Pokemon
from domain.stat import Stat


class PokemonRepository(Protocol):
    def get_random_pokemon(self) -> Pokemon:
        ...


class RandomStatSelector(Protocol):
    def select(self) -> Stat:
        ...


class GameService:
    def __init__(self, pokemon_repository: PokemonRepository, stat_selector: RandomStatSelector):
        self.pokemon_repository = pokemon_repository
        self.stat_selector = stat_selector

    def start_game(self) -> Game:
        pokemon = self.pokemon_repository.get_random_pokemon()
        game = Game(pokemon=pokemon)
        random_stat = self.stat_selector.select()
        game.add_stat_hint(random_stat)
        return game
