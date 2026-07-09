from sqlmodel import Field, Relationship, SQLModel

# Import at runtime so SA can resolve the target
from .email import Email  # noqa: F401


class Attachment(SQLModel, table=True):
    __tablename__ = "attachments"

    id: int | None = Field(default=None, primary_key=True)
    filename: str
    email_id: int = Field(foreign_key="emails.id", nullable=False)

    email: Email = Relationship(back_populates="attachments")
