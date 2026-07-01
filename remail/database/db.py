from pathlib import Path

from sqlmodel import create_engine

# Prefer using pattern_kit's singleton/provider if available; otherwise
# fall back to a simple lazy engine wrapper so behavior is deterministic
# and tests (which monkeypatch `remail.database.engine`) continue to work.
try:
    import pattern_kit as _pk  # type: ignore
except Exception:
    _pk = None


DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"
database_url = f"sqlite:///{DB_PATH}"


def _make_engine() -> object:
    return create_engine(database_url, echo=False)


if _pk is not None:
    # Try common singleton/provider API names from pattern_kit
    Singleton = getattr(_pk, "Singleton", None) or getattr(_pk, "singleton", None)
    Provider = getattr(_pk, "Provider", None) or getattr(_pk, "provider", None)
    if Singleton and callable(Singleton):
        try:

            @Singleton
            def _engine_factory():
                return _make_engine()

            engine = _engine_factory()
        except Exception:
            engine = _make_engine()
    elif Provider and callable(Provider):
        try:
            engine = Provider(_make_engine)
        except Exception:
            engine = _make_engine()
    else:
        engine = _make_engine()
else:
    # Lazy wrapper: create engine on first attribute access. This keeps the
    # module-level `engine` name available for monkeypatching in tests.
    class _LazyEngine:
        __slots__ = ("_engine",)

        def __init__(self):
            self._engine = None

        def _ensure(self):
            if self._engine is None:
                self._engine = _make_engine()

        def __getattr__(self, item):
            self._ensure()
            return getattr(self._engine, item)

        def __repr__(self) -> str:  # pragma: no cover - trivial
            if self._engine is None:
                return "<LazyEngine (not created)>"
            return repr(self._engine)

    engine = _LazyEngine()
