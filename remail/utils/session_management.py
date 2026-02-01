import contextvars
from functools import wraps
from inspect import signature

from sqlmodel import Session

from remail.database import engine

# ContextVar speichert die aktuell aktive Session pro Task / Thread
_current_session: contextvars.ContextVar[Session | None] = contextvars.ContextVar(
    "current_session", default=None
)


def session(func):
    sig = signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)

        provided_session = bound.arguments.get("session")
        parent_session = _current_session.get()

        owns_session = False
        # Fall 1: Session explizit übergeben
        if provided_session is not None:
            active_session = provided_session

        # Fall 2: Parent-@session existiert → gleiche nehmen
        elif parent_session is not None:
            active_session = parent_session
            if "session" in sig.parameters:
                kwargs["session"] = active_session

        # Fall 3: Neue Root-Session erzeugen
        else:
            active_session = Session(engine)
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
            print("Debug: Rolling back session because exception occurred")
            active_session.rollback()
            raise e
        finally:
            if owns_session:
                _current_session.reset(token)
                active_session.flush()
                active_session.close()

    return wrapper
