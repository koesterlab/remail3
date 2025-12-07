from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, TypeVar
from weakref import WeakMethod, WeakSet

E = TypeVar("E", bound=Enum)


class ObservableState(Generic[E]):  # noqa: UP046
    def __init__(self) -> None:
        self._values: dict[E, Any] = {}
        self._weak_observers: dict[E, WeakSet[Callable[[Any], None] | WeakMethod]] = {}
        self._strong_observers: dict[E, set[Callable[[Any], None]]] = {}

    def register_observer(
        self, prop: E, callback: Callable[[Any], None], weak: bool = False
    ) -> None:
        """Registriert einen Observer für eine Property."""
        if weak:
            if prop not in self._weak_observers:
                self._weak_observers[prop] = WeakSet()
            if hasattr(callback, "__self__") and hasattr(callback, "__func__"):
                self._weak_observers[prop].add(WeakMethod(callback))
            else:
                self._weak_observers[prop].add(callback)
        else:
            if prop not in self._strong_observers:
                self._strong_observers[prop] = set()
            self._strong_observers[prop].add(callback)

    def set(self, prop: E, value: Any) -> None:
        if prop in self._values and value == self._values[prop]:
            return
        self._values[prop] = value
        # schwache Observer
        self.trigger(prop)

    def get(self, prop: E) -> Any:
        return self._values.get(prop, None)

    def trigger(self, prop: E) -> None:
        value = self._values[prop]
        if prop in self._weak_observers:
            dead = []
            for obs in self._weak_observers[prop]:
                if isinstance(obs, WeakMethod):
                    func = obs()
                    if func is not None:
                        func(value)
                    else:
                        dead.append(obs)
                else:
                    obs(value)
            for d in dead:
                self._weak_observers[prop].discard(d)
        # starke Observer
        if prop in self._strong_observers:
            for obs in self._strong_observers[prop]:
                obs(value)
