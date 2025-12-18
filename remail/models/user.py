from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.enums import Protocol

if TYPE_CHECKING:
    from .chat_session import ChatSession


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(
        sa_column=sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    )
    password: str
    protocol: Protocol = Field(
        sa_column=sqlalchemy.Column(sqlalchemy.Enum(Protocol), nullable=False)
    )
    last_refresh: datetime | None = None

    # Relationships
    chat_sessions: list["ChatSession"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
