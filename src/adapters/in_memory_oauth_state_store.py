import time


class InMemoryOAuthStateStore:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self._states: dict[str, float] = {}
        self._ttl_seconds = ttl_seconds

    async def save(self, state: str) -> None:
        self._states[state] = time.monotonic()

    async def consume(self, state: str) -> bool:
        created = self._states.pop(state, None)
        if created is None:
            return False
        return (time.monotonic() - created) < self._ttl_seconds
