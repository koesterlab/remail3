#!/usr/bin/env python3
"""Initialize SQLite database and create all tables from SQLModel models."""

import os
from pathlib import Path

from sqlmodel import SQLModel, create_engine

import remail.models  # noqa: F401


def init_database(db_path: str = "database.db") -> None:
    """
    Initialize the SQLite database and create all tables.

    Args:
        db_path: Path to the database file (default: database.db)
    """

    db_file = Path(db_path).resolve()

    db_file.parent.mkdir(parents=True, exist_ok=True)

    database_url = f"sqlite:///{db_file}"
    engine = create_engine(database_url, echo=True)

    print(f"\n{'=' * 80}")
    print(f"Initializing SQLite database at: {db_file}")
    print(f"{'=' * 80}\n")

    SQLModel.metadata.create_all(engine)

    print(f"\n{'=' * 80}")
    print("✅ Database initialized successfully!")
    print(f"{'=' * 80}\n")

    print("Created tables:")

    for table in SQLModel.metadata.sorted_tables:
        print(f"  - {table.name}")

    print(f"\nDatabase location: {db_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize SQLite database and create tables")
    parser.add_argument(
        "--db-path",
        "-d",
        default="database.db",
        help="Path to the database file (default: database.db)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Delete existing database before creating new one",
    )

    args = parser.parse_args()

    if args.force and os.path.exists(args.db_path):
        print(f"🗑️  Removing existing database: {args.db_path}")
        os.remove(args.db_path)

    # Initialize the database
    init_database(args.db_path)
