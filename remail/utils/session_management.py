import contextvars
from collections.abc import Callable
from functools import wraps
from inspect import signature

from sqlmodel import Session

# ContextVar speichert die aktuell aktive Session pro Task / Thread
_current_session: contextvars.ContextVar[Session | None] = contextvars.ContextVar(
    "current_session", default=None
)


def session(func: Callable) -> Callable:
    """
    Decorator that creates a database session for every function call. If the method is called by another @session method, the Session from the calling methode is used
    The session can be accessed via the parameter session
    """
    sig = signature(func)

    @wraps(func)
    def wrapper(*args, session: Session | None = None, **kwargs):
        provided_session = session
        parent_session = _current_session.get()

        owns_session = False
        # Fall 1: Session explizit übergeben
        if provided_session is not None:
            active_session = provided_session
            kwargs["session"] = active_session

        # Fall 2: Parent-@session existiert → gleiche nehmen
        elif parent_session is not None:
            active_session = parent_session
            if "session" in sig.parameters:
                kwargs["session"] = active_session

        # Fall 3: Neue Root-Session erzeugen
        else:
            # Import the engine dynamically so tests can monkeypatch
            # `remail.database.engine` (conftest.patch_db_engine).
            import remail.database as _database

            active_session = Session(_database.engine)
            if "session" in sig.parameters:
                kwargs["session"] = active_session
            owns_session = True

        token = _current_session.set(active_session)

        try:
            result = func(*args, **kwargs)
            if owns_session:
                active_session.commit()
            return result
        except Exception as e:
            if owns_session:
                print("Debug: Rolling back session because exception occurred")
                print(e)
                active_session.rollback()
            raise
        finally:
            if owns_session:
                _current_session.reset(token)
                active_session.flush()
                active_session.close()

    return wrapper
