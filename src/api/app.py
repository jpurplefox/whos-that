from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from litestar import Litestar

from api.dependencies import container
from api.views import router


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncIterator[None]:
    await container.init_resources()  # type: ignore[misc]
    yield
    await container.shutdown_resources()  # type: ignore[misc]


app = Litestar(
    route_handlers=[router],
    lifespan=[lifespan],
)
