import pytest

from domain.exceptions import AlreadyConsultedThisTurn, GameOver, NotEnoughBattery
from domain.game import Comparison, ComparisonHint, Game, StatHint
from domain.pokemon import Pokemon
from domain.stat import Stat


def test_game_starts_with_no_hints():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon)
    assert game.hints == []


def test_add_hint_returns_hint_with_stat_and_value():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon)

    hint = game.add_stat_hint(Stat.HP)

    assert hint == StatHint(stat=Stat.HP, value=45)


def test_add_hint_appends_to_hints_list():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon)

    game.add_stat_hint(Stat.HP)
    game.add_stat_hint(Stat.ATTACK)

    assert len(game.hints) == 2
    assert game.hints[0] == StatHint(stat=Stat.HP, value=45)
    assert game.hints[1] == StatHint(stat=Stat.ATTACK, value=49)


def test_guess_returns_true_when_correct():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=bulbasaur)

    result = game.guess(bulbasaur)

    assert result is True
    assert len(game.hints) == 0


def test_guess_returns_false_when_incorrect():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    game = Game(pokemon=bulbasaur)

    result = game.guess(charmander)

    assert result is False


def test_guess_adds_to_attempts():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    game = Game(pokemon=bulbasaur)

    game.guess(charmander)

    assert len(game.attempts) == 1
    assert game.attempts[0] == charmander


def test_guess_raises_when_no_attempts_remaining():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    game = Game(pokemon=bulbasaur, max_attempts=1)

    game.guess(charmander)

    with pytest.raises(GameOver):
        game.guess(charmander)


def test_guess_adds_comparison_hint():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
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


def test_consult_stat_subtracts_battery_and_adds_hint():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon, battery=100, max_battery=100)

    hint = game.consult_stat(Stat.HP, cost=30)

    assert game.battery == 70
    assert game.consulted_this_turn is True
    assert hint == StatHint(stat=Stat.HP, value=45)
    assert hint in game.hints


def test_consult_stat_raises_already_consulted_this_turn():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon, battery=100, max_battery=100)

    game.consult_stat(Stat.HP, cost=30)

    with pytest.raises(AlreadyConsultedThisTurn):
        game.consult_stat(Stat.ATTACK, cost=30)


def test_consult_stat_raises_not_enough_battery():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon, battery=10, max_battery=100)

    with pytest.raises(NotEnoughBattery):
        game.consult_stat(Stat.HP, cost=30)


def test_available_stats_excludes_used_stats():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=pokemon)

    game.add_stat_hint(Stat.HP)
    game.add_stat_hint(Stat.ATTACK)

    available = game.available_stats
    assert Stat.HP not in available
    assert Stat.ATTACK not in available
    assert Stat.DEFENSE in available
    assert Stat.SP_ATTACK in available
    assert Stat.SP_DEFENSE in available
    assert Stat.SPEED in available


def test_guess_recovers_battery_and_resets_consulted():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    game = Game(pokemon=pokemon, battery=70, max_battery=100, battery_recovery=10)
    game.consulted_this_turn = True

    game.guess(charmander)

    assert game.battery == 80
    assert game.consulted_this_turn is False


def test_consult_stat_raises_game_over_when_won():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    game = Game(pokemon=bulbasaur, battery=100, max_battery=100)
    game.guess(bulbasaur)
    assert game.is_won

    with pytest.raises(GameOver):
        game.consult_stat(Stat.HP, cost=30)


def test_consult_stat_raises_game_over_when_no_attempts_remaining():
    bulbasaur = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    game = Game(pokemon=bulbasaur, max_attempts=1, battery=100, max_battery=100)
    game.guess(charmander)
    assert game.attempts_remaining == 0

    with pytest.raises(GameOver):
        game.consult_stat(Stat.HP, cost=30)


def test_guess_battery_does_not_exceed_max():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45, image_url="https://example.com/bulbasaur.png")
    charmander = Pokemon(id=4, name="Charmander", hp=39, attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65, image_url="https://example.com/charmander.png")
    game = Game(pokemon=pokemon, battery=95, max_battery=100, battery_recovery=10)

    game.guess(charmander)

    assert game.battery == 100
