from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Awaitable

from pydantic import BaseModel

if TYPE_CHECKING:
    from domain.game import Game


class DomainEvent(BaseModel):
    """Base class for all domain events."""
    model_config = {"arbitrary_types_allowed": True}


class GameWon(DomainEvent):
    """Emitted when a game is won."""
    game: Game


# Rebuild model to resolve forward reference
from domain.game import Game  # noqa: E402
GameWon.model_rebuild()


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """Simple in-memory event bus for domain events."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None:
        """Register a handler for an event type."""
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers."""
        handlers = self._handlers[type(event)]
        for handler in handlers:
            await handler(event)
