"""from pathlib import Path

from sqlmodel import create_engine

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"
database_url = f"sqlite:///{DB_PATH}"
engine = create_engine(database_url, echo=True)"""

from pathlib import Path

import sqlite_vec
from sqlalchemy import event
from sqlmodel import create_engine

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"
database_url = f"sqlite:///{DB_PATH}"

# Create an engine (with multi-threading support for Flet)
engine = create_engine(database_url, echo=False, connect_args={"check_same_thread": False})

# Set up the event listener
@event.listens_for(engine, "connect")
def load_sqlite_vec_extension(dbapi_conn, connection_record):
    # This code is executed automatically for EVERY new database connection.
    dbapi_conn.enable_load_extension(True)
    sqlite_vec.load(dbapi_conn)
    dbapi_conn.enable_load_extension(False)
