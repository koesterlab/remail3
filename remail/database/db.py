import importlib
from pathlib import Path
from types import ModuleType
from typing import Any

from sqlalchemy import event
from sqlmodel import create_engine

# Tip tanımlaması
sqlite_vec: ModuleType | None = None

try:
    sqlite_vec = importlib.import_module("sqlite_vec")
except Exception:  # pragma: no cover
    sqlite_vec = None

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"
database_url = f"sqlite:///{DB_PATH}"

# Create an engine (with multi-threading support for Flet)
engine = create_engine(database_url, echo=False, connect_args={"check_same_thread": False})

# Set up the event listener
@event.listens_for(engine, "connect")
def load_sqlite_vec_extension(dbapi_conn: Any, connection_record: Any) -> None:
    dbapi_conn.enable_load_extension(True)
    if sqlite_vec is not None:
        sqlite_vec.load(dbapi_conn)
    dbapi_conn.enable_load_extension(False)
