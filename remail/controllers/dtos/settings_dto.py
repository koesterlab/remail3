"""Data Transfer Object for application settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SettingsDTO:
    """DTO for application settings."""

    id: int
    theme_mode: str
    font_size: str
    font_family: str
    language: str
    timezone: str
    desktop_notifications: bool
    email_notifications: bool
    quiet_hours: bool

    @classmethod
    def from_model(cls, settings) -> SettingsDTO:
        """
        Create DTO from Settings model.

        Args:
            settings: Settings model instance

        Returns:
            SettingsDTO instance
        """
        return cls(
            id=settings.id,
            theme_mode=settings.theme_mode,
            font_size=settings.font_size,
            font_family=settings.font_family,
            language=settings.language,
            timezone=settings.timezone,
            desktop_notifications=settings.desktop_notifications,
            email_notifications=settings.email_notifications,
            quiet_hours=settings.quiet_hours,
        )

    def to_dict(self) -> dict[str, str | int | bool]:
        """Convert DTO to dictionary."""
        return {
            "id": self.id,
            "theme_mode": self.theme_mode,
            "font_size": self.font_size,
            "font_family": self.font_family,
            "language": self.language,
            "timezone": self.timezone,
            "desktop_notifications": self.desktop_notifications,
            "email_notifications": self.email_notifications,
            "quiet_hours": self.quiet_hours,
        }
