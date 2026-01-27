import pytest
from litestar.testing import TestClient

from api.app import app
from api.dependencies import container
from domain.exceptions import GameNotFound, NoAttemptsRemaining, PokemonNotFound
from domain.game import Game
from domain.pokemon import Pokemon
from domain.stat import Stat


@pytest.fixture
def pikachu():
    return Pokemon(
        id=25,
        name="pikachu",
        hp=35,
        attack=55,
        defense=40,
        sp_attack=50,
        sp_defense=50,
        speed=90,
    )


@pytest.fixture
def bulbasaur():
    return Pokemon(
        id=1,
        name="bulbasaur",
        hp=45,
        attack=49,
        defense=49,
        sp_attack=65,
        sp_defense=65,
        speed=45,
    )


class FakeStartGame:
    def __init__(self, game: Game):
        self.game = game

    async def execute(self) -> Game:
        return self.game


class FakeGetGame:
    def __init__(self, game: Game):
        self.game = game

    async def execute(self, game_id: str) -> Game:
        return self.game


class FakeGetGameNotFound:
    async def execute(self, game_id: str) -> Game:
        raise GameNotFound()


class FakeGuess:
    def __init__(self, game: Game):
        self.game = game

    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        return self.game


def test_create_game_returns_game_with_hint(pikachu: Pokemon):
    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)

    with container.start_game.override(FakeStartGame(game)):
        with TestClient(app) as client:
            response = client.post("/games")

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "game-1"
    assert data["is_won"] is False
    assert data["attempts_remaining"] == 4
    assert data["attempts"] == []
    assert len(data["hints"]) == 1
    assert data["hints"][0]["type"] == "stat"
    assert data["hints"][0]["stat"] == "speed"
    assert data["hints"][0]["value"] == 90


def test_guess_correct_pokemon(pikachu: Pokemon):
    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)
    game.guess(pikachu)

    with container.guess.override(FakeGuess(game)):
        with TestClient(app) as client:
            response = client.post(
                "/games/game-1/guess",
                json={"pokemon_name": "pikachu"},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["is_won"] is True
    assert data["attempts_remaining"] == 3
    assert data["attempts"] == ["pikachu"]


def test_guess_incorrect_pokemon_returns_comparison_hint(
    pikachu: Pokemon,
    bulbasaur: Pokemon,
):
    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)
    game.guess(bulbasaur)

    with container.guess.override(FakeGuess(game)):
        with TestClient(app) as client:
            response = client.post(
                "/games/game-1/guess",
                json={"pokemon_name": "bulbasaur"},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["is_won"] is False
    assert data["attempts_remaining"] == 3
    assert data["attempts"] == ["bulbasaur"]
    assert len(data["hints"]) == 2
    assert data["hints"][1]["type"] == "comparison"
    assert data["hints"][1]["pokemon"] == "bulbasaur"
    assert data["hints"][1]["comparisons"]["speed"] == "higher"


class FakeGuessNoAttempts:
    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        raise NoAttemptsRemaining()


def test_guess_returns_400_when_no_attempts_remaining():
    with container.guess.override(FakeGuessNoAttempts()):
        with TestClient(app) as client:
            response = client.post(
                "/games/game-1/guess",
                json={"pokemon_name": "pikachu"},
            )

    assert response.status_code == 400


class FakeGuessPokemonNotFound:
    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        raise PokemonNotFound()


def test_guess_returns_400_when_pokemon_not_found():
    with container.guess.override(FakeGuessPokemonNotFound()):
        with TestClient(app) as client:
            response = client.post(
                "/games/game-1/guess",
                json={"pokemon_name": "notapokemon"},
            )

    assert response.status_code == 400


def test_guess_returns_400_when_pokemon_name_is_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/games/game-1/guess",
            json={"pokemon_name": "../pikachu"},
        )

    assert response.status_code == 400


class FakeGuessGameNotFound:
    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        raise GameNotFound()


def test_guess_returns_404_when_game_not_found():
    with container.guess.override(FakeGuessGameNotFound()):
        with TestClient(app) as client:
            response = client.post(
                "/games/nonexistent/guess",
                json={"pokemon_name": "pikachu"},
            )

    assert response.status_code == 404


def test_guess_returns_400_when_invalid_json():
    with TestClient(app) as client:
        response = client.post(
            "/games/game-1/guess",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 400


def test_get_game_returns_game(pikachu: Pokemon):
    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)

    with container.get_game.override(FakeGetGame(game)):
        with TestClient(app) as client:
            response = client.get("/games/game-1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "game-1"
    assert data["is_won"] is False
    assert data["attempts_remaining"] == 4
    assert data["attempts"] == []
    assert len(data["hints"]) == 1
    assert data["hints"][0]["type"] == "stat"
    assert data["hints"][0]["stat"] == "speed"
    assert data["hints"][0]["value"] == 90


def test_get_game_returns_404_when_not_found():
    with container.get_game.override(FakeGetGameNotFound()):
        with TestClient(app) as client:
            response = client.get("/games/nonexistent")

    assert response.status_code == 404
