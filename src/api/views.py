from litestar import Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi.datastructures import ResponseSpec
from litestar.params import Dependency

from api.dependencies import get_consult_pokedex, get_get_game, get_guess, get_start_game
from api.schemas import GameResponse, GuessRequest
from domain.exceptions import (
    AlreadyConsultedThisTurn,
    GameNotFound,
    GameOver,
    NoStatsAvailable,
    NotEnoughBattery,
    PokemonNotFound,
)
from services.consult_pokedex import ConsultPokedex
from services.get_game import GetGame
from services.guess import Guess
from services.start_game import StartGame


@post("/games")
async def create_game(
    start_game: StartGame = Dependency(skip_validation=True),
) -> GameResponse:
    game = await start_game.execute()
    return GameResponse.from_game(game)


@get(
    "/games/{game_id:str}",
    responses={404: ResponseSpec(data_container=None, description="Game not found")},
)
async def get_game(
    game_id: str,
    get_game_use_case: GetGame = Dependency(skip_validation=True),
) -> GameResponse:
    try:
        game = await get_game_use_case.execute(game_id)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameResponse.from_game(game)


@post(
    "/games/{game_id:str}/consult",
    responses={
        400: ResponseSpec(data_container=None, description="Not enough battery, already consulted this turn, or no stats available"),
        404: ResponseSpec(data_container=None, description="Game not found"),
    },
)
async def consult(
    game_id: str,
    consult_pokedex: ConsultPokedex = Dependency(skip_validation=True),
) -> GameResponse:
    try:
        game = await consult_pokedex.execute(game_id)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")
    except NotEnoughBattery:
        raise HTTPException(status_code=400, detail="Not enough battery")
    except AlreadyConsultedThisTurn:
        raise HTTPException(status_code=400, detail="Already consulted this turn")
    except NoStatsAvailable:
        raise HTTPException(status_code=400, detail="No stats available")
    except GameOver:
        raise HTTPException(status_code=400, detail="Game is over")

    return GameResponse.from_game(game)


@post(
    "/games/{game_id:str}/guess",
    responses={
        400: ResponseSpec(data_container=None, description="Game is over or pokemon not found"),
        404: ResponseSpec(data_container=None, description="Game not found"),
    },
)
async def guess(
    game_id: str,
    data: GuessRequest,
    guess_use_case: Guess = Dependency(skip_validation=True),
) -> GameResponse:
    try:
        game = await guess_use_case.execute(game_id, data.pokemon_name)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")
    except GameOver:
        raise HTTPException(status_code=400, detail="Game is over")
    except PokemonNotFound:
        raise HTTPException(status_code=400, detail="Pokemon not found")

    return GameResponse.from_game(game)


router = Router(
    path="/",
    route_handlers=[create_game, get_game, consult, guess],
    dependencies={
        "start_game": Provide(get_start_game),
        "guess_use_case": Provide(get_guess),
        "get_game_use_case": Provide(get_get_game),
        "consult_pokedex": Provide(get_consult_pokedex),
    },
)
