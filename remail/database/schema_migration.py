"""Small database schema migrations for existing local SQLite databases."""

from sqlalchemy import Engine, text


def ensure_settings_columns(engine: Engine) -> None:
    """Ensure settings table contains local Ollama settings columns.

    SQLModel's create_all creates missing tables, but it does not add new
    columns to existing tables. This function adds the required columns for
    existing local development databases.
    """
    with engine.begin() as connection:
        existing_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(settings)"))
        }

        if not existing_columns:
            return

        if "ollama_base_url" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE settings "
                    "ADD COLUMN ollama_base_url TEXT "
                    "DEFAULT 'http://localhost:11434'"
                )
            )

        if "selected_local_model" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE settings "
                    "ADD COLUMN selected_local_model TEXT"
                )
            )