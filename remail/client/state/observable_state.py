from __future__ import annotations

from enum import Enum
from typing import Any, Generic, TypeVar

from pattern_kit import Event

E = TypeVar("E", bound=Enum)


class ObservableState(Generic[E]):  # noqa: UP046
    """State management using pattern_kit.Event for clean event handling."""

    def __init__(self) -> None:
        self._values: dict[E, Any] = {}
        self._events: dict[E, Event] = {}

    def _get_or_create_event(self, prop: E) -> Event:
        """Get or create an Event for a property."""
        if prop not in self._events:
            self._events[prop] = Event()
        return self._events[prop]

    def register_observer(
        self, prop: E, callback: callable, weak: bool = False
    ) -> None:
        """
        Register an observer callback for a property using pattern_kit.Event.
        The 'weak' parameter is accepted for backward compatibility but has no effect
        as pattern_kit.Event manages references automatically.
        """
        event = self._get_or_create_event(prop)
        event += callback

    def unregister_observer(
        self, prop: E, callback: callable
    ) -> None:
        """Unregister an observer callback for a property."""
        event = self._get_or_create_event(prop)
        event -= callback

    def set(self, prop: E, value: Any) -> None:
        """Set a property value and trigger observers."""
        if prop in self._values and value == self._values[prop]:
            return
        self._values[prop] = value
        self.trigger(prop)

    def get(self, prop: E) -> Any:
        """Get a property value."""
        return self._values.get(prop, None)

    def trigger(self, prop: E) -> None:
        """Trigger all observers for a property with its current value."""
        event = self._get_or_create_event(prop)
        value = self._values.get(prop)
        event(value)

