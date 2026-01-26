from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from api import views
from api.containers import Container
from api.exceptions import InvalidJSONBody
from api.schemas import ErrorResponse


container = Container()


async def invalid_json_body_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(ErrorResponse(error="Invalid JSON").to_dict(), status_code=400)


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    await container.init_resources()  # type: ignore[misc]
    yield
    await container.shutdown_resources()  # type: ignore[misc]


routes = [
    Route("/games", views.create_game, methods=["POST"]),
    Route("/games/{game_id}/guess", views.guess, methods=["POST"]),
]

container.wire(modules=[views])
app = Starlette(
    routes=routes,
    lifespan=lifespan,
    exception_handlers={InvalidJSONBody: invalid_json_body_handler},
)
