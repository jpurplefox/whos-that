from typing import Protocol


class OAuthStateStore(Protocol):
    async def save(self, state: str) -> None: ...

    async def consume(self, state: str) -> bool: ...
