from dependency_injector.wiring import inject, Provide
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.containers import Container
from api.schemas import GameResponse, GuessRequest
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
    body = await request.json()

    try:
        guess_request = GuessRequest(**body)
    except ValidationError as e:
        return JSONResponse({"errors": e.errors()}, status_code=422)

    try:
        game = await guess_use_case.execute(game_id, guess_request.pokemon_name)
    except GameNotFound:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    except NoAttemptsRemaining:
        return JSONResponse({"error": "No attempts remaining"}, status_code=422)
    except PokemonNotFound:
        return JSONResponse({"error": "Pokemon not found"}, status_code=422)

    return JSONResponse(GameResponse.from_game(game).model_dump())
