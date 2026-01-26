from dependency_injector.wiring import inject, Provide
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from api.containers import Container
from api.schemas import GameResponse
from services.game_service import GameService


@inject
async def create_game(
    request: Request,
    game_service: GameService = Provide[Container.game_service],
) -> JSONResponse:
    game = await game_service.start_game()
    return JSONResponse(GameResponse.from_game(game).model_dump())


@inject
async def guess(
    request: Request,
    game_service: GameService = Provide[Container.game_service],
) -> JSONResponse:
    game_id = request.path_params["game_id"]
    body = await request.json()
    pokemon_name = body["pokemon_name"]

    game = await game_service.guess(game_id, pokemon_name)
    return JSONResponse(GameResponse.from_game(game).model_dump())


routes = [
    Route("/games", create_game, methods=["POST"]),
    Route("/games/{game_id}/guess", guess, methods=["POST"]),
]

container = Container()
container.wire(modules=[__name__])

app = Starlette(routes=routes)
