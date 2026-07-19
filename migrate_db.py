#!/usr/bin/env python3
"""Initialize the SQLite database by running Alembic migrations to head."""

import os
from pathlib import Path

from alembic.config import Config

from alembic import command
from remail.database.db import DB_PATH

REPO_ROOT = Path(__file__).resolve().parent


def init_database() -> None:
    """Run Alembic migrations to bring the database up to the latest revision."""

    alembic_cfg = Config(str(REPO_ROOT / "alembic.ini"))

    print(f"\n{'=' * 80}")
    print(f"Running Alembic migrations for database at: {DB_PATH}")
    print(f"{'=' * 80}\n")

    command.upgrade(alembic_cfg, "head")

    print(f"\n{'=' * 80}")
    print("✅ Database initialized successfully!")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize the database via Alembic migrations")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Delete the existing database before migrating",
    )

    args = parser.parse_args()

    if args.init and DB_PATH.exists():
        print(f"🗑️  Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)

    init_database()
