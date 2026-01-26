from dependency_injector.wiring import inject, Provide
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from api.containers import Container
from api.schemas import GameResponse
from domain.exceptions import NoAttemptsRemaining, PokemonNotFound
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
    pokemon_name = body["pokemon_name"]

    try:
        game = await guess_use_case.execute(game_id, pokemon_name)
    except NoAttemptsRemaining:
        return JSONResponse({"error": "No attempts remaining"}, status_code=422)
    except PokemonNotFound:
        return JSONResponse({"error": "Pokemon not found"}, status_code=422)

    return JSONResponse(GameResponse.from_game(game).model_dump())


routes = [
    Route("/games", create_game, methods=["POST"]),
    Route("/games/{game_id}/guess", guess, methods=["POST"]),
]

container = Container()
container.wire(modules=[__name__])

app = Starlette(routes=routes)
