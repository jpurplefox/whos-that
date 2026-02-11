import pytest

from domain.exceptions import (
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
    assert hint in game.hints


def test_consult_allows_multiple_hints_per_turn(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=100, max_battery=100)
    hint1 = StatHint.create(bulbasaur, Stat.HP)
    hint2 = StatHint.create(bulbasaur, Stat.ATTACK)

    game.consult(hint1, cost=30)
    game.consult(hint2, cost=30)

    assert game.battery == 40
    assert hint1 in game.hints
    assert hint2 in game.hints


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


def test_guess_recovers_battery(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, battery=70, max_battery=100, battery_recovery=10)

    game.guess(charmander)

    assert game.battery == 80


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
    assert game.battery == 70
    # battery_pct = 70/100 = 0.7, base = 1000 + 3000 + 700 = 4700
    assert game.score == 4700


def test_score_matches_issue_example(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=60, max_battery=100, battery_recovery=10)

    game.guess(charmander)
    game.guess(bulbasaur)

    assert game.is_won is True
    assert game.attempts_remaining == 2
    assert game.battery == 70
    # battery_pct = 70/100 = 0.7, base = 1000 + 2000 + 700 = 3700
    assert game.score == 3700


def test_score_on_first_attempt_win(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=90, max_battery=100, battery_recovery=10)

    game.guess(bulbasaur)

    # battery_pct = 90/100 = 0.9, base = 1000 + 3000 + 900 = 4900
    assert game.score == 4900


def test_score_on_last_attempt_win(
    bulbasaur: Pokemon, charmander: Pokemon
) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=2, battery=50, max_battery=100, battery_recovery=10)

    game.guess(charmander)
    game.guess(bulbasaur)

    assert game.attempts_remaining == 0
    assert game.is_won is True
    # battery = 60 (50 + 10 recovery from wrong guess), battery_pct = 60/100 = 0.6
    # base = 1000 + 0 + 600 = 1600
    assert game.score == 1600


def test_score_with_zero_battery_on_win(bulbasaur: Pokemon) -> None:
    game = Game(pokemon=bulbasaur, max_attempts=4, battery=0, max_battery=100, battery_recovery=0)

    game.guess(bulbasaur)

    # battery_pct = 0/100 = 0, base = 1000 + 3000 + 0 = 4000
    assert game.score == 4000


def test_zero_battery_zero_attempts_win_scores_above_zero(bulbasaur: Pokemon) -> None:
    game = Game(
        pokemon=bulbasaur,
        max_attempts=1,
        battery=0,
        max_battery=100,
        battery_recovery=0,
        initial_battery=75,
        difficulty_multiplier=2.0,
    )

    game.guess(bulbasaur)

    assert game.is_won is True
    assert game.attempts_remaining == 0
    assert game.battery == 0
    # battery_pct = 0/75 = 0, base = 1000 + 0 + 0 = 1000, score = 1000 * 2.0 = 2000
    assert game.score == 2000
    assert game.score > 0


def test_hard_perfect_scores_higher_than_easy_perfect(bulbasaur: Pokemon) -> None:
    easy_perfect = Game(
        pokemon=bulbasaur,
        max_attempts=5,
        battery=100,
        max_battery=100,
        battery_recovery=35,
        initial_battery=100,
        difficulty_multiplier=1.0,
    )
    easy_perfect.guess(bulbasaur)

    hard_perfect = Game(
        pokemon=bulbasaur,
        max_attempts=4,
        battery=75,
        max_battery=100,
        battery_recovery=20,
        initial_battery=75,
        difficulty_multiplier=2.0,
    )
    hard_perfect.guess(bulbasaur)

    assert easy_perfect.score == 6000
    assert hard_perfect.score == 10000
    assert hard_perfect.score > easy_perfect.score


def test_max_scores_match_expected_values(bulbasaur: Pokemon) -> None:
    # Easy: 5 attempts, 100 battery, multiplier 1.0 - first guess win
    easy = Game(
        pokemon=bulbasaur,
        max_attempts=5,
        battery=100,
        max_battery=100,
        initial_battery=100,
        difficulty_multiplier=1.0,
    )
    easy.guess(bulbasaur)

    # Medium: 4 attempts, 100 battery, multiplier 1.5 - first guess win
    medium = Game(
        pokemon=bulbasaur,
        max_attempts=4,
        battery=100,
        max_battery=100,
        initial_battery=100,
        difficulty_multiplier=1.5,
    )
    medium.guess(bulbasaur)

    # Hard: 4 attempts, 75 battery, multiplier 2.0 - first guess win
    hard = Game(
        pokemon=bulbasaur,
        max_attempts=4,
        battery=75,
        max_battery=100,
        initial_battery=75,
        difficulty_multiplier=2.0,
    )
    hard.guess(bulbasaur)

    # base_easy = 1000 + 4*1000 + 1000 = 6000, * 1.0 = 6000
    assert easy.score == 6000
    # base_medium = 1000 + 3*1000 + 1000 = 5000, * 1.5 = 7500
    assert medium.score == 7500
    # base_hard = 1000 + 3*1000 + 1000 = 5000, * 2.0 = 10000
    assert hard.score == 10000


def test_loss_still_scores_zero(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    game = Game(
        pokemon=bulbasaur,
        max_attempts=1,
        battery=75,
        max_battery=100,
        initial_battery=75,
        difficulty_multiplier=2.0,
    )

    game.guess(charmander)

    assert game.is_over is True
    assert game.is_won is False
    assert game.score == 0


def test_in_progress_score_is_none(bulbasaur: Pokemon) -> None:
    game = Game(
        pokemon=bulbasaur,
        max_attempts=4,
        battery=75,
        initial_battery=75,
        difficulty_multiplier=2.0,
    )

    assert game.is_over is False
    assert game.score is None


def test_medium_perfect_score(bulbasaur: Pokemon) -> None:
    game = Game(
        pokemon=bulbasaur,
        max_attempts=4,
        battery=100,
        max_battery=100,
        initial_battery=100,
        difficulty_multiplier=1.5,
    )

    game.guess(bulbasaur)

    # base = 1000 + 3*1000 + 1000 = 5000, * 1.5 = 7500
    assert game.score == 7500


def test_min_win_scores(bulbasaur: Pokemon, charmander: Pokemon) -> None:
    # Easy min: last attempt (5th), 0 battery
    easy_min = Game(
        pokemon=bulbasaur,
        max_attempts=1,
        battery=0,
        max_battery=100,
        battery_recovery=0,
        initial_battery=100,
        difficulty_multiplier=1.0,
    )
    easy_min.guess(bulbasaur)

    # Hard min: last attempt, 0 battery
    hard_min = Game(
        pokemon=bulbasaur,
        max_attempts=1,
        battery=0,
        max_battery=100,
        battery_recovery=0,
        initial_battery=75,
        difficulty_multiplier=2.0,
    )
    hard_min.guess(bulbasaur)

    # Easy min: base = 1000 + 0 + 0 = 1000, * 1.0 = 1000
    assert easy_min.score == 1000
    # Hard min: base = 1000 + 0 + 0 = 1000, * 2.0 = 2000
    assert hard_min.score == 2000


def test_score_with_zero_initial_battery(bulbasaur: Pokemon) -> None:
    """Edge case: initial_battery=0 should not cause division by zero."""
    game = Game(
        pokemon=bulbasaur,
        max_attempts=4,
        battery=0,
        max_battery=100,
        battery_recovery=0,
        initial_battery=0,
        difficulty_multiplier=1.0,
    )

    game.guess(bulbasaur)

    # battery_pct = 0 (guard clause), base = 1000 + 3000 + 0 = 4000
    assert game.score == 4000
