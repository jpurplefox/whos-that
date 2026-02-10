import time
from collections import defaultdict
from typing import Any

from litestar import Request, Response
from litestar.types import ASGIApp, Receive, Scope, Send


class RateLimitState:
    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        if len(self._requests[key]) >= max_requests:
            return False
        self._requests[key].append(now)
        return True


_state = RateLimitState()

# Limits: exact path -> (max_requests, window_seconds)
_RATE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/games": (30, 3600),                 # 30 game creations per hour
    "/api/auth/google/callback": (10, 3600),  # 10 auth attempts per hour
}


def _get_client_ip(scope: "Scope") -> str:
    """Extract client IP from ASGI scope, with X-Forwarded-For support."""
    headers = dict(scope.get("headers", []))
    forwarded = headers.get(b"x-forwarded-for", b"").decode()
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = scope.get("client")
    if client:
        return client[0]
    return "unknown"


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope["path"]
        method: str = scope["method"]

        # Only rate-limit POST requests to exact paths
        if method == "POST" and path in _RATE_LIMITS:
            max_req, window = _RATE_LIMITS[path]
            ip = _get_client_ip(scope)
            key = f"{ip}:{path}"
            if not _state.is_allowed(key, max_req, window):
                response = Response(
                    content={"detail": "Too many requests"},
                    status_code=429,
                )
                response_scope = response.to_asgi_response(
                    app=None,  # type: ignore[arg-type]
                    request=Request(scope=scope),
                )
                await response_scope(scope, receive, send)
                return

        await self.app(scope, receive, send)
