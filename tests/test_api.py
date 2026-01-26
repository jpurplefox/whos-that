import pytest
from starlette.testclient import TestClient

from api.app import app, container
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


class FakeGuess:
    def __init__(self, game: Game):
        self.game = game

    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        return self.game


def test_create_game_returns_game_with_hint(pikachu: Pokemon):
    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)

    with container.start_game.override(FakeStartGame(game)):
        client = TestClient(app)
        response = client.post("/games")

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


def test_guess_correct_pokemon(pikachu: Pokemon):
    game = Game(pokemon=pikachu, id="game-1")
    game.add_stat_hint(Stat.SPEED)
    game.guess(pikachu)

    with container.guess.override(FakeGuess(game)):
        client = TestClient(app)
        response = client.post(
            "/games/game-1/guess",
            json={"pokemon_name": "pikachu"},
        )

    assert response.status_code == 200
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
        client = TestClient(app)
        response = client.post(
            "/games/game-1/guess",
            json={"pokemon_name": "bulbasaur"},
        )

    assert response.status_code == 200
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


def test_guess_returns_422_when_no_attempts_remaining():
    with container.guess.override(FakeGuessNoAttempts()):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/games/game-1/guess",
            json={"pokemon_name": "pikachu"},
        )

    assert response.status_code == 422
    assert response.json() == {"error": "No attempts remaining"}


class FakeGuessPokemonNotFound:
    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        raise PokemonNotFound()


def test_guess_returns_422_when_pokemon_not_found():
    with container.guess.override(FakeGuessPokemonNotFound()):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/games/game-1/guess",
            json={"pokemon_name": "notapokemon"},
        )

    assert response.status_code == 422
    assert response.json() == {"error": "Pokemon not found"}


def test_guess_returns_422_when_pokemon_name_is_invalid():
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/games/game-1/guess",
        json={"pokemon_name": "../pikachu"},
    )

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "Validation error"
    assert "details" in data


class FakeGuessGameNotFound:
    async def execute(self, game_id: str, pokemon_name: str) -> Game:
        raise GameNotFound()


def test_guess_returns_404_when_game_not_found():
    with container.guess.override(FakeGuessGameNotFound()):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/games/nonexistent/guess",
            json={"pokemon_name": "pikachu"},
        )

    assert response.status_code == 404
    assert response.json() == {"error": "Game not found"}


def test_guess_returns_400_when_invalid_json():
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/games/game-1/guess",
        content="not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid JSON"}
