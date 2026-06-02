"""Join table for Email and Tag."""

from sqlmodel import Field, SQLModel


class EmailTag(SQLModel, table=True):
    """Links emails with their tags"""

    __tablename__ = "email_tag"

    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    email_id: int = Field(foreign_key="emails.id", primary_key=True)
