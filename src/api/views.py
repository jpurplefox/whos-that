from litestar import Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi.datastructures import ResponseSpec
from litestar.params import Dependency

from api.dependencies import get_get_game, get_guess, get_start_game
from api.schemas import GameResponse, GuessRequest
from domain.exceptions import GameNotFound, NoAttemptsRemaining, PokemonNotFound
from services.get_game import GetGame
from services.guess import Guess
from services.start_game import StartGame


@post("/games")
async def create_game(
    start_game: StartGame = Dependency(skip_validation=True),
) -> GameResponse:
    game = await start_game.execute()
    return GameResponse.from_game(game)


@post(
    "/games/{game_id:str}/guess",
    responses={
        400: ResponseSpec(data_container=None, description="No attempts remaining or pokemon not found"),
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
    except NoAttemptsRemaining:
        raise HTTPException(status_code=400, detail="No attempts remaining")
    except PokemonNotFound:
        raise HTTPException(status_code=400, detail="Pokemon not found")

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


router = Router(
    path="/",
    route_handlers=[create_game, guess, get_game],
    dependencies={
        "start_game": Provide(get_start_game),
        "guess_use_case": Provide(get_guess),
        "get_game_use_case": Provide(get_get_game),
    },
)
