from dependency_injector.wiring import inject, Provide
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.containers import Container
from api.helpers import parse_json_body
from api.schemas import ErrorResponse, GameResponse, GuessRequest
from domain.exceptions import GameNotFound, NoAttemptsRemaining, PokemonNotFound
from services.guess import Guess
from services.start_game import StartGame


@inject
async def create_game(
    request: Request,
    start_game: StartGame = Provide[Container.start_game],
) -> JSONResponse:
    game = await start_game.execute()
    return JSONResponse(GameResponse.from_game(game).model_dump())


@inject
async def guess(
    request: Request,
    guess_use_case: Guess = Provide[Container.guess],
) -> JSONResponse:
    game_id = request.path_params["game_id"]
    body = await parse_json_body(request)

    try:
        guess_request = GuessRequest(**body)
    except ValidationError as e:
        error = ErrorResponse(error="Validation error", details=e.errors())
        return JSONResponse(error.to_dict(), status_code=422)

    try:
        game = await guess_use_case.execute(game_id, guess_request.pokemon_name)
    except GameNotFound:
        return JSONResponse(ErrorResponse(error="Game not found").to_dict(), status_code=404)
    except NoAttemptsRemaining:
        return JSONResponse(ErrorResponse(error="No attempts remaining").to_dict(), status_code=422)
    except PokemonNotFound:
        return JSONResponse(ErrorResponse(error="Pokemon not found").to_dict(), status_code=422)

    return JSONResponse(GameResponse.from_game(game).model_dump())
