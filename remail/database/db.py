"""Database engine configuration."""

from pathlib import Path

from sqlmodel import create_engine

# Database file path
DB_PATH = Path("database.db").resolve()

# Create database engine
database_url = f"sqlite:///{DB_PATH}"
engine = create_engine(database_url, echo=False)
