from pathlib import Path

from sqlmodel import create_engine
from remail.database.schema_migration import ensure_settings_columns

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"
database_url = f"sqlite:///{DB_PATH}"
engine = create_engine(database_url, echo=False)
ensure_settings_columns(engine)