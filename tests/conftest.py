import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture()
def test_engine():
    """Create a fresh in-memory database engine for a test."""
    import remail.models  # noqa: F401

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def patch_db_engine(test_engine, monkeypatch):
    """Patch all database engine references to use the test engine."""
    import remail.utils.session_management as session_management
    import remail.database
    remail.database.engine = test_engine
    # Prevent leaked @session context between tests when a session is provided.
    session_management._current_session.set(None)
    yield
    session_management._current_session.set(None)


# Single-test isolated session bound to the shared test engine
@pytest.fixture()
def session(test_engine):
    with Session(test_engine) as s:
        yield s


@pytest.fixture()
def test_session(test_engine):
    """Alias for session fixture to match existing test names."""
    with Session(test_engine) as s:
        yield s
