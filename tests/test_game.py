import pytest

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


def test_guess_returns_true_when_correct():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=bulbasaur)

    result = game.guess(bulbasaur)

    assert result is True


def test_guess_returns_false_when_incorrect():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65)
    game = Game(pokemon=bulbasaur)

    result = game.guess(charmander)

    assert result is False


def test_guess_adds_to_attempts():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65)
    game = Game(pokemon=bulbasaur)

    game.guess(charmander)

    assert len(game.attempts) == 1
    assert game.attempts[0] == charmander


def test_guess_raises_when_no_attempts_remaining():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65)
    game = Game(pokemon=bulbasaur, max_attempts=1)

    game.guess(charmander)

    with pytest.raises(ValueError, match="No attempts remaining"):
        game.guess(charmander)
