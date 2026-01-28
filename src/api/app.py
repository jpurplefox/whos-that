from typing import Any

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


def _handle_serialization_error(_: "Request[Any, Any, Any]", exc: SerializationException) -> "Response[Any]":
    return Response(
        content={"status_code": 400, "detail": exc.detail},
        status_code=400,
    )


async def _on_startup() -> None:
    await container.init_resources()


async def _on_shutdown() -> None:
    await container.shutdown_resources()


app = Litestar(
    route_handlers=[router],
    exception_handlers={SerializationException: _handle_serialization_error},
    on_startup=[_on_startup],
    on_shutdown=[_on_shutdown],
)
