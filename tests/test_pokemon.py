from domain.pokemon import Pokemon
from domain.stat import Stat


def test_get_stat_hp():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    assert pokemon.get_stat(Stat.HP) == 45


def test_get_stat_attack():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    assert pokemon.get_stat(Stat.ATTACK) == 49


def test_get_stat_defense():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    assert pokemon.get_stat(Stat.DEFENSE) == 49


def test_get_stat_sp_attack():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    assert pokemon.get_stat(Stat.SP_ATTACK) == 65


def test_get_stat_sp_defense():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    assert pokemon.get_stat(Stat.SP_DEFENSE) == 65


def test_get_stat_speed():
    pokemon = Pokemon(id=1, name="Bulbasaur", hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45)
    assert pokemon.get_stat(Stat.SPEED) == 45
