from typing import Optional
from sqlmodel import Field, SQLModel


class EmailChunk(SQLModel, table=True):
    """Speichert die zerschnittenen Text-Chunks einer E-Mail samt Vektor-Embedding."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Verknüpfung zur originalen E-Mail (Fremdschlüssel)
    email_id: int = Field(foreign_key="email.id")

    # Die Reihenfolge des Chunks (0, 1, 2...)
    chunk_index: int

    # Der Inhalt des Chunks
    content: str

    # Das Vektor-Embedding (sqlite-vec speichert Vektoren am besten als BLOB/Bytes)
    embedding: bytes