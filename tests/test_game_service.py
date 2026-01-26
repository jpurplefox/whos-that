from copy import deepcopy

import pytest

from domain.game import Game, StatHint
from domain.pokemon import Pokemon
from domain.stat import Stat
from services.game_service import GameService


class FakePokemonRepository:
    def __init__(self) -> None:
        self.pokemons_by_name: dict[str, Pokemon] = {}

    async def get_by_name(self, name: str) -> Pokemon:
        return self.pokemons_by_name[name]

    def add_pokemon(self, pokemon: Pokemon) -> None:
        self.pokemons_by_name[pokemon.name] = pokemon


class FakeStatSelector:
    def __init__(self, stat: Stat):
        self.stat = stat

    def select(self) -> Stat:
        return self.stat


class FakePokemonSelector:
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon

    async def select(self) -> Pokemon:
        return self.pokemon


class FakeGameRepository:
    def __init__(self) -> None:
        self.games: dict[str, Game] = {}
        self.next_id = 1

    async def save(self, game: Game) -> Game:
        if game.id is None:
            game.id = str(self.next_id)
            self.next_id += 1
        self.games[game.id] = deepcopy(game)
        return game

    async def get(self, game_id: str) -> Game:
        return deepcopy(self.games[game_id])


@pytest.mark.asyncio
async def test_start_game_creates_game_with_pokemon():
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    pokemon_repository = FakePokemonRepository()
    stat_selector = FakeStatSelector(Stat.SPEED)
    game_repository = FakeGameRepository()
    pokemon_selector = FakePokemonSelector(pokemon)

    service = GameService(pokemon_repository, stat_selector, game_repository, pokemon_selector)
    game = await service.start_game()

    assert game.pokemon == pokemon


@pytest.mark.asyncio
async def test_start_game_adds_first_hint_with_selected_stat():
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    pokemon_repository = FakePokemonRepository()
    stat_selector = FakeStatSelector(Stat.SPEED)
    game_repository = FakeGameRepository()
    pokemon_selector = FakePokemonSelector(pokemon)

    service = GameService(pokemon_repository, stat_selector, game_repository, pokemon_selector)
    game = await service.start_game()

    assert len(game.hints) == 1
    assert game.hints[0] == StatHint(stat=Stat.SPEED, value=90)


@pytest.mark.asyncio
async def test_start_game_saves_game_with_id():
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    pokemon_repository = FakePokemonRepository()
    stat_selector = FakeStatSelector(Stat.SPEED)
    game_repository = FakeGameRepository()
    pokemon_selector = FakePokemonSelector(pokemon)

    service = GameService(pokemon_repository, stat_selector, game_repository, pokemon_selector)
    game = await service.start_game()

    assert game.id is not None


@pytest.mark.asyncio
async def test_guess_returns_game_with_attempt():
    pikachu = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65)
    pokemon_repository = FakePokemonRepository()
    pokemon_repository.add_pokemon(charmander)
    stat_selector = FakeStatSelector(Stat.SPEED)
    game_repository = FakeGameRepository()
    pokemon_selector = FakePokemonSelector(pikachu)

    service = GameService(pokemon_repository, stat_selector, game_repository, pokemon_selector)
    game = await service.start_game()
    game = await service.guess(game.id, "Charmander")

    assert len(game.attempts) == 1
    assert game.attempts[0] == charmander
