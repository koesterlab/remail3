from typing import TypeVar, Generic, Callable, Dict, Any
from enum import Enum
from weakref import WeakSet, WeakMethod

E = TypeVar("E", bound=Enum)

class ObservableState(Generic[E]):
    def __init__(self):
        self._values: Dict[E, Any] = {}
        # Zwei Listen pro Property: schwach und stark
        self._weak_observers: Dict[E, WeakSet] = {}
        self._strong_observers: Dict[E, set] = {}

    def register_observer(self, prop: E, callback: Callable[[Any], None], weak: bool = False) -> None:
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
