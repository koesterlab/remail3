#!/usr/bin/env python3
"""Initialize SQLite database and create all tables from SQLModel models."""

import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

import remail.models  # noqa: F401
from remail.fixtures import load_conversation_fixtures


def init_database(db_path: str = "database.db", load_fixtures: bool = False) -> None:
    """
    Initialize the SQLite database and create all tables.

    Args:
        db_path: Path to the database file (default: database.db)
        load_fixtures: Whether to load sample fixture data (default: False)
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

    # Load fixtures if requested
    if load_fixtures:
        print("\n" + "=" * 80)
        print("Loading Fixtures")
        print("=" * 80 + "\n")

        with Session(engine) as session:
            try:
                load_conversation_fixtures(session)
                print("✅ All fixtures loaded successfully!\n")
            except Exception as e:
                print(f"❌ Error loading fixtures: {e}\n")
                session.rollback()
                raise


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
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Load sample fixture data into the database",
    )

    args = parser.parse_args()

    if args.force and os.path.exists(args.db_path):
        print(f"🗑️  Removing existing database: {args.db_path}")
        os.remove(args.db_path)

    # Initialize the database
    init_database(args.db_path, load_fixtures=args.fixtures)
