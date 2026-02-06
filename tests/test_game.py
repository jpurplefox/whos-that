import pytest

from domain.exceptions import (
    AlreadyConsultedThisTurn,
    GameOver,
    HintAlreadyRevealed,
    NotEnoughBattery,
)
from domain.game import Game
from domain.hint import Comparison, ComparisonHint, FullyEvolvedHint, Hint, StatHint
from domain.hint_factory import FullyEvolvedHintCreator
from domain.pokemon import Pokemon
from domain.stat import Stat


def test_game_starts_with_no_hints(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur)
    assert game.hints == []


def test_stat_hint_create(bulbasaur: Pokemon) -> None:
    hint = StatHint.create(bulbasaur, Stat.HP)

    assert hint == StatHint(stat=Stat.HP, value=45)


def test_stat_hint_available_stats(bulbasaur: Pokemon) -> None:
    hints: list[Hint] = [
        StatHint.create(bulbasaur, Stat.HP),
        StatHint.create(bulbasaur, Stat.ATTACK),
    ]

    available = StatHint.available_stats(hints)

    assert Stat.HP not in available
    assert Stat.ATTACK not in available
    assert Stat.DEFENSE in available
    assert Stat.SP_ATTACK in available
    assert Stat.SP_DEFENSE in available
    assert Stat.SPEED in available


def test_guess_returns_true_when_correct(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur)

    result = game.guess(bulbasaur)

    assert result is True
    assert len(game.hints) == 0


def test_guess_returns_false_when_incorrect(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur)

    result = game.guess(charmander)

    assert result is False


def test_guess_adds_to_attempts(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur)

    game.guess(charmander)

    assert len(game.attempts) == 1
    assert game.attempts[0] == charmander


def test_guess_raises_when_no_attempts_remaining(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=1)

    game.guess(charmander)

    with pytest.raises(GameOver):
        game.guess(charmander)


def test_guess_adds_comparison_hint(bulbasaur: Pokemon, charmander: Pokemon) -> None:
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


def test_consult_subtracts_battery_and_adds_hint(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=100, max_battery=100)
    hint = StatHint.create(bulbasaur, Stat.HP)

    game.consult(hint, cost=30)

    assert game.battery == 70
    assert game.consulted_this_turn is True
    assert hint in game.hints


def test_consult_raises_already_consulted_this_turn(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=100, max_battery=100)
    hint1 = StatHint.create(bulbasaur, Stat.HP)
    hint2 = StatHint.create(bulbasaur, Stat.ATTACK)

    game.consult(hint1, cost=30)

    with pytest.raises(AlreadyConsultedThisTurn):
        game.consult(hint2, cost=30)


def test_consult_raises_not_enough_battery(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=10, max_battery=100)
    hint = StatHint.create(bulbasaur, Stat.HP)

    with pytest.raises(NotEnoughBattery):
        game.consult(hint, cost=30)


def test_consult_raises_hint_already_revealed(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=100, max_battery=100)
    hint = StatHint.create(bulbasaur, Stat.HP)
    game.hints.append(hint)

    duplicate_hint = StatHint.create(bulbasaur, Stat.HP)

    with pytest.raises(HintAlreadyRevealed):
        game.consult(duplicate_hint, cost=30)


def test_guess_recovers_battery_and_resets_consulted(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=70, max_battery=100, battery_recovery=10)
    game.consulted_this_turn = True

    game.guess(charmander)

    assert game.battery == 80
    assert game.consulted_this_turn is False


def test_consult_raises_game_over_when_won(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=100, max_battery=100)
    game.guess(bulbasaur)
    assert game.is_won
    hint = StatHint.create(bulbasaur, Stat.HP)

    with pytest.raises(GameOver):
        game.consult(hint, cost=30)


def test_consult_raises_game_over_when_no_attempts_remaining(
    bulbasaur: Pokemon, charmander: Pokemon
) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=1, battery=100, max_battery=100)
    game.guess(charmander)
    assert game.attempts_remaining == 0
    hint = StatHint.create(bulbasaur, Stat.HP)

    with pytest.raises(GameOver):
        game.consult(hint, cost=30)


def test_guess_battery_does_not_exceed_max(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=95, max_battery=100, battery_recovery=10)

    game.guess(charmander)

    assert game.battery == 100


def test_fully_evolved_hint_create_with_fully_evolved_pokemon(raichu: Pokemon) -> None:
    hint = FullyEvolvedHint.create(raichu)

    assert hint.is_fully_evolved is True


def test_fully_evolved_hint_create_with_non_fully_evolved_pokemon(pikachu: Pokemon) -> None:
    hint = FullyEvolvedHint.create(pikachu)

    assert hint.is_fully_evolved is False


def test_fully_evolved_hint_is_available_when_not_revealed(pikachu: Pokemon) -> None:
    hints: list[Hint] = [StatHint.create(pikachu, Stat.HP)]
    creator = FullyEvolvedHintCreator()

    assert creator.is_available(pikachu, hints) is True


def test_fully_evolved_hint_is_not_available_when_already_revealed(pikachu: Pokemon) -> None:
    hints: list[Hint] = [FullyEvolvedHint.create(pikachu)]
    creator = FullyEvolvedHintCreator()

    assert creator.is_available(pikachu, hints) is False


def test_score_is_none_when_game_in_progress(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur)

    assert game.score is None


def test_score_is_zero_when_game_lost(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=1, battery=80, max_battery=100)

    game.guess(charmander)

    assert game.is_over is True
    assert game.is_won is False
    assert game.score == 0


def test_score_is_zero_when_lost_regardless_of_battery(
    bulbasaur: Pokemon, charmander: Pokemon
) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=1, battery=100, max_battery=100)

    game.guess(charmander)

    assert game.score == 0


def test_score_when_won_with_remaining_attempts_and_battery(
    bulbasaur: Pokemon,
) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=70, max_battery=100, battery_recovery=10)

    game.guess(bulbasaur)

    assert game.is_won is True
    assert game.attempts_remaining == 3
    assert game.battery == 80
    assert game.score == 3800


def test_score_matches_issue_example(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=60, max_battery=100, battery_recovery=10)

    game.guess(charmander)
    game.guess(bulbasaur)

    assert game.is_won is True
    assert game.attempts_remaining == 2
    assert game.battery == 80
    assert game.score == 2800


def test_score_on_first_attempt_win(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=90, max_battery=100, battery_recovery=10)

    game.guess(bulbasaur)

    assert game.score == 4000


def test_score_on_last_attempt_win(
    bulbasaur: Pokemon, charmander: Pokemon
) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=2, battery=50, max_battery=100, battery_recovery=10)

    game.guess(charmander)
    game.guess(bulbasaur)

    assert game.attempts_remaining == 0
    assert game.is_won is True
    assert game.score == 700


def test_score_with_zero_battery_on_win(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=0, max_battery=100, battery_recovery=0)

    game.guess(bulbasaur)

    assert game.score == 3000
