import pytest

from domain.game import Comparison, ComparisonHint, Game, StatHint
from domain.pokemon import Pokemon
from domain.stat import Stat


def test_game_starts_with_no_hints():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=pokemon)
    assert game.hints == []


def test_add_hint_returns_hint_with_stat_and_value():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=pokemon)

    hint = game.add_stat_hint(Stat.HP)

    assert hint == StatHint(stat=Stat.HP, value=45)


def test_add_hint_appends_to_hints_list():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=pokemon)

    game.add_stat_hint(Stat.HP)
    game.add_stat_hint(Stat.ATTACK)

    assert len(game.hints) == 2
    assert game.hints[0] == StatHint(stat=Stat.HP, value=45)
    assert game.hints[1] == StatHint(stat=Stat.ATTACK, value=49)


def test_guess_returns_true_when_correct():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    game = Game(pokemon=bulbasaur)

    result = game.guess(bulbasaur)

    assert result is True
    assert len(game.hints) == 0


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


def test_guess_adds_comparison_hint():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65)
    game = Game(pokemon=bulbasaur)

    game.guess(charmander)

    assert len(game.hints) == 1
    hint = game.hints[0]
    assert isinstance(hint, ComparisonHint)
    assert hint.pokemon == charmander
    assert hint.comparisons[Stat.HP] == Comparison.HIGHER
    assert hint.comparisons[Stat.ATTACK] == Comparison.LOWER
    assert hint.comparisons[Stat.DEFENSE] == Comparison.HIGHER
    assert hint.comparisons[Stat.SP_ATTACK] == Comparison.HIGHER
    assert hint.comparisons[Stat.SP_DEFENSE] == Comparison.HIGHER
    assert hint.comparisons[Stat.SPEED] == Comparison.LOWER
