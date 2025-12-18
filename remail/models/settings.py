"""Settings model for application preferences."""

from sqlmodel import Field, SQLModel


class Settings(SQLModel, table=True):
    """Application settings model with single-row constraint."""

    __tablename__ = "settings"

    id: int = Field(default=1, primary_key=True)
    theme_mode: str = Field(default="system")
    font_size: str = Field(default="medium")
    font_family: str = Field(default="system")
    language: str = Field(default="en")
    timezone: str = Field(default="Europe/London")
    desktop_notifications: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    quiet_hours: bool = Field(default=False)
