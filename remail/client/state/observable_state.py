from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, TypeVar
from weakref import WeakMethod, WeakSet

E = TypeVar("E", bound=Enum)


# This module prefers using `pattern_kit` when available. If it's not
# installed or doesn't expose a compatible API, we fall back to the
# original in-repo implementation so behavior remains unchanged.
try:
    import pattern_kit as _pk  # type: ignore
except Exception:
    _pk = None


def _call(subject: Any, names: list[str], *args, **kwargs):
    """Call the first available method name on subject from names."""
    for n in names:
        fn = getattr(subject, n, None)
        if callable(fn):
            return fn(*args, **kwargs)
    raise AttributeError(f"No suitable method found on {subject!r} among {names}")


class ObservableState(Generic[E]):  # noqa: UP046
    def __init__(self) -> None:
        # If pattern_kit is available and provides a Subject/Observable
        # we will use one per property and delegate calls. The exact
        # method names may vary across `pattern_kit` versions, so we
        # try a few common ones and fall back to the builtin
        # implementation below.
        self._use_pattern_kit = False
        self._pk_subjects: dict[E, Any] = {}
        if _pk is not None:
            # try to find a Subject/Observable class and verify its API
            subj_cls = getattr(_pk, "Subject", None) or getattr(_pk, "Observable", None)
            if subj_cls is not None:
                # instantiate a temporary subject and check for a compatible API
                try:
                    tmp = subj_cls()
                    has_subscribe = callable(getattr(tmp, "subscribe", None))
                    has_on_next = callable(getattr(tmp, "on_next", None))
                    has_get = (
                        callable(getattr(tmp, "get", None))
                        or hasattr(tmp, "value")
                        or hasattr(tmp, "current")
                    )
                    if has_subscribe and (has_on_next or has_get):
                        self._pk_subjects = {}
                        self._pk_subject_cls = subj_cls
                        self._use_pattern_kit = True
                except Exception:
                    # pattern_kit exists but API not compatible; fall back
                    self._use_pattern_kit = False

        # Fallback internal structures (kept if pattern_kit not available)
        self._values: dict[E, Any] = {}
        self._weak_observers: dict[E, WeakSet[Callable[[Any], None] | WeakMethod]] = {}
        self._strong_observers: dict[E, set[Callable[[Any], None]]] = {}

    def register_observer(
        self, prop: E, callback: Callable[[Any], None], weak: bool = False
    ) -> None:
        """Register an observer for a property.

        If `pattern_kit` is present it will be used; otherwise the
        in-repo observer logic is used.
        """
        if self._use_pattern_kit:
            if prop not in self._pk_subjects:
                self._pk_subjects[prop] = self._pk_subject_cls()
            subj = self._pk_subjects[prop]
            # try common subscribe method names
            for name in ("subscribe", "attach", "observe"):
                fn = getattr(subj, name, None)
                if callable(fn):
                    fn(callback)
                    return
            # last resort: try `on_next` like Rx-style
            if hasattr(subj, "on_next"):
                # we create a tiny wrapper to call callback when new value
                def _cb(v):
                    callback(v)

                subj.on_next = _cb  # type: ignore
                return

        # Fallback to original implementation
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
        if self._use_pattern_kit:
            if prop not in self._pk_subjects:
                self._pk_subjects[prop] = self._pk_subject_cls()
            subj = self._pk_subjects[prop]
            # try common push/notify method names
            for name in ("on_next", "notify", "push", "set"):
                fn = getattr(subj, name, None)
                if callable(fn):
                    fn(value)
                    return
            # unable to push via pattern_kit instance; fall back

        if prop in self._values and value == self._values[prop]:
            return
        self._values[prop] = value
        self.trigger(prop)

    def get(self, prop: E) -> Any:
        if self._use_pattern_kit and prop in self._pk_subjects:
            subj = self._pk_subjects[prop]
            for name in ("get", "value", "current"):
                fn = getattr(subj, name, None)
                if callable(fn):
                    return fn()
            # try attribute access
            if hasattr(subj, "value"):
                return subj.value
        return self._values.get(prop, None)

    def trigger(self, prop: E) -> None:
        # Only used by the fallback implementation
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
        if prop in self._strong_observers:
            for obs in list(self._strong_observers[prop]):
                obs(value)
