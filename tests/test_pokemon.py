from domain.pokemon import Pokemon
from domain.stat import Stat


def test_get_stat_hp(bulbasaur: Pokemon) -> None:
    assert bulbasaur.get_stat(Stat.HP) == 45


def test_get_stat_attack(bulbasaur: Pokemon) -> None:
    assert bulbasaur.get_stat(Stat.ATTACK) == 49


def test_get_stat_defense(bulbasaur: Pokemon) -> None:
    assert bulbasaur.get_stat(Stat.DEFENSE) == 49


def test_get_stat_sp_attack(bulbasaur: Pokemon) -> None:
    assert bulbasaur.get_stat(Stat.SP_ATTACK) == 65


def test_get_stat_sp_defense(bulbasaur: Pokemon) -> None:
    assert bulbasaur.get_stat(Stat.SP_DEFENSE) == 65


def test_get_stat_speed(bulbasaur: Pokemon) -> None:
    assert bulbasaur.get_stat(Stat.SPEED) == 45


def test_is_fully_evolved_false_when_has_evolutions(pikachu: Pokemon) -> None:
    assert pikachu.is_fully_evolved is False


def test_is_fully_evolved_true_when_no_evolutions(raichu: Pokemon) -> None:
    assert raichu.is_fully_evolved is True
