"""Settings model for application preferences."""

from sqlmodel import Field, SQLModel


class Settings(SQLModel, table=True):
    """Application settings model with single-row constraint."""

    __tablename__ = "settings"

    id: int = Field(default=1, primary_key=True)
    theme_mode: str = Field(default="system")
    font_size: str = Field(default="medium")
    font_family: str = Field(default="Arial")
    language: str = Field(default="English")
    timezone: str = Field(default="europe-berlin")
    desktop_notifications: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    quiet_hours: bool = Field(default=False)
    llm_url: str = Field(default="http://localhost:11434/v1")
    llm_key: str = Field(default="ollama")
