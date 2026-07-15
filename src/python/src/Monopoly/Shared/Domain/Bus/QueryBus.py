"""Query bus. Exactly one handler per query type. Returns result. Always in-process."""

from collections.abc import Callable
from typing import Any, TypeVar, cast

Q = TypeVar("Q")
R = TypeVar("R")


class QueryBus:
    """Dispatches queries to registered handlers. One handler per query type."""

    def __init__(self) -> None:
        self._handlers: dict[type, Callable[[Any], Any]] = {}

    def subscribe(self, queryType: type[Q], handler: Callable[[Q], R]) -> None:
        self._handlers[queryType] = handler

    def ask(self, query: Q) -> R:  # type: ignore[type-var]
        handler = self._handlers.get(type(query))
        if handler is None:
            raise ValueError(f"No handler registered for {type(query).__name__}")
        return cast(R, handler(query))
