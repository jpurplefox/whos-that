from domain.game import Hint
from domain.pokemon import Pokemon
from domain.stat import Stat
from services.game_service import GameService


class FakePokemonRepository:
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon

    def get_random_pokemon(self) -> Pokemon:
        return self.pokemon


class FakeStatSelector:
    def __init__(self, stat: Stat):
        self.stat = stat

    def select(self) -> Stat:
        return self.stat


def test_start_game_creates_game_with_pokemon():
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = FakePokemonRepository(pokemon)
    stat_selector = FakeStatSelector(Stat.SPEED)

    service = GameService(repository, stat_selector)
    game = service.start_game()

    assert game.pokemon == pokemon


def test_start_game_adds_first_hint_with_selected_stat():
    pokemon = Pokemon(id=25, name="Pikachu", hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90)
    repository = FakePokemonRepository(pokemon)
    stat_selector = FakeStatSelector(Stat.SPEED)

    service = GameService(repository, stat_selector)
    game = service.start_game()

    assert len(game.hints) == 1
    assert game.hints[0] == Hint(stat=Stat.SPEED, value=90)
