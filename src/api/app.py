from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Route

from api import views
from api.containers import Container


container = Container()


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
app = Starlette(routes=routes, lifespan=lifespan)
