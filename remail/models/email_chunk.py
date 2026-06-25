from sqlmodel import Field, SQLModel


class EmailChunk(SQLModel, table=False):
    """Stores the split text chunks of an email together with their vector embedding."""

    id: int | None = Field(default=None, primary_key=True)

    # Reference to the original email
    email_id: int = Field(foreign_key="email.id")

    # The order of the chunk
    chunk_index: int

    # The content of the chunk
    content: str

    embedding: bytes
