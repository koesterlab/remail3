from sqlmodel import Field


def id_field(table_name: str | None = None):
    """
    Create a standard auto-incrementing primary key field.

    Args:
        table_name: Optional table name (kept for API compatibility but not used with SQLite)

    Returns:
        A Field configured as an auto-incrementing primary key
    """
    return Field(default=None, primary_key=True)
