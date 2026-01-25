from domain.game import Game, Hint
from domain.pokemon import Pokemon
from domain.stat import Stat


def test_game_starts_with_no_hints():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=pokemon)
    assert game.hints == []


def test_add_hint_returns_hint_with_stat_and_value():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=pokemon)

    hint = game.add_hint(Stat.HP)

    assert hint == Hint(stat=Stat.HP, value=45)


def test_add_hint_appends_to_hints_list():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=pokemon)

    game.add_hint(Stat.HP)
    game.add_hint(Stat.ATTACK)

    assert len(game.hints) == 2
    assert game.hints[0] == Hint(stat=Stat.HP, value=45)
    assert game.hints[1] == Hint(stat=Stat.ATTACK, value=49)
