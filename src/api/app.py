from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
from litestar import Litestar, Request, Response
from litestar.exceptions import SerializationException
from sentry_sdk.integrations.litestar import LitestarIntegration

from api.dependencies import container
from api.views import router
from config import Settings
from structlog_config import configure_logging

configure_logging()

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


def _handle_serialization_error(_: Request, exc: SerializationException) -> Response:
    return Response(
        content={"status_code": 400, "detail": exc.detail},
        status_code=400,
    )


app = Litestar(
    route_handlers=[router],
    lifespan=[lifespan],
    exception_handlers={SerializationException: _handle_serialization_error},
)
