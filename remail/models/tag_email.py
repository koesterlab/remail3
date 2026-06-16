"""Join table linking emails and tags."""

from sqlmodel import Field, SQLModel


class EmailTag(SQLModel, table=True):
    """Many-to-many link between emails and tags."""

    __tablename__ = "tag_email"

    email_id: int = Field(foreign_key="emails.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
