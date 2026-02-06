from collections import defaultdict
from typing import Awaitable, Callable, TypeVar, cast

from pydantic import BaseModel

from domain.game import Game
from structlog_config import get_logger

logger = get_logger()


class DomainEvent(BaseModel):
    """Base class for all domain events."""
    model_config = {"arbitrary_types_allowed": True}


class GameWon(DomainEvent):
    """Emitted when a game is won."""
    game: Game


T = TypeVar("T", bound=DomainEvent)
EventHandler = Callable[[T], Awaitable[None]]
ErrorHandler = Callable[..., object]


class EventBus:
    """Simple in-memory event bus for domain events."""

    def __init__(self, on_error: ErrorHandler | None = None) -> None:
        self._handlers: dict[type, list[EventHandler[DomainEvent]]] = defaultdict(list)
        self._on_error = on_error

    def subscribe(self, event_type: type[T], handler: EventHandler[T]) -> None:
        """Register a handler for an event type."""
        self._handlers[event_type].append(cast(EventHandler[DomainEvent], handler))

    async def publish(self, event: T) -> None:
        """Publish an event to all registered handlers."""
        handlers = cast(list[EventHandler[T]], self._handlers[type(event)])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.exception("event_handler_failed", event_type=type(event).__name__)
                if self._on_error:
                    self._on_error(e)
