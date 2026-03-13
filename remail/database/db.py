import logging
from pathlib import Path

from sqlalchemy import event
from sqlmodel import create_engine, Session

DB_PATH = Path("database.db").resolve()
database_url = f"sqlite:///{DB_PATH}"
engine = create_engine(database_url, echo=False)