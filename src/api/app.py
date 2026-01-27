from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
from litestar import Litestar
from sentry_sdk.integrations.litestar import LitestarIntegration

from api.dependencies import container
from api.views import router
from config import Settings

_settings = Settings()
if _settings.sentry_dsn:
    sentry_sdk.init(
        dsn=_settings.sentry_dsn,
        traces_sample_rate=_settings.sentry_traces_sample_rate,
        integrations=[LitestarIntegration()],
    )


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncIterator[None]:
    await container.init_resources()  # type: ignore[misc]
    yield
    await container.shutdown_resources()  # type: ignore[misc]


app = Litestar(
    route_handlers=[router],
    lifespan=[lifespan],
)
