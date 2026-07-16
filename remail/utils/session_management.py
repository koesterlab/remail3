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
    def wrapper(*args, **kwargs):
        bound_args = sig.bind_partial(*args, **kwargs)
        provided_session = bound_args.arguments.get("session")
        parent_session = _current_session.get()

        owns_session = False
        if provided_session is not None:
            active_session = provided_session
        elif parent_session is not None:
            active_session = parent_session
        else:
            from remail.database import engine as db_engine

            active_session = Session(db_engine, expire_on_commit=False)
            owns_session = True

        if "session" in sig.parameters and "session" not in bound_args.arguments:
            kwargs["session"] = active_session

        token = _current_session.set(active_session)

        try:
            result = func(*args, **kwargs)
            if owns_session:
                active_session.commit()
            return result
        except Exception:
            if owns_session:
                active_session.rollback()
            raise
        finally:
            if owns_session:
                _current_session.reset(token)
                active_session.close()

    return wrapper
