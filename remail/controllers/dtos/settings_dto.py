"""Data Transfer Object for application settings."""

from __future__ import annotations

from dataclasses import dataclass

from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone
from remail.models import Settings
from remail.utils.session_management import session


@dataclass(slots=True, frozen=False)
class SettingsDTO:
    """DTO for application settings."""

    id: int
    theme_mode: ThemeMode
    font_size: FontSize
    font_family: FontFamily
    language: Language
    timezone: Timezone
    desktop_notifications: bool
    email_notifications: bool
    quiet_hours: bool
    llm_url: str
    llm_key: str

    @classmethod
    @session
    def from_model(cls, settings: Settings) -> SettingsDTO:
        """
        Create DTO from Settings model.

        Args:
            settings: Settings model instance

        Returns:
            SettingsDTO instance
        """
        return SettingsDTO(
            id=settings.id,
            theme_mode=ThemeMode(settings.theme_mode),
            font_size=FontSize(settings.font_size),
            font_family=FontFamily(settings.font_family),
            language=Language(settings.language),
            timezone=Timezone(settings.timezone),
            desktop_notifications=settings.desktop_notifications,
            email_notifications=settings.email_notifications,
            quiet_hours=settings.quiet_hours,
            llm_url=settings.llm_url,
            llm_key=settings.llm_key,
        )
