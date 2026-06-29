"""Data Transfer Object for application settings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone
from remail.models import Settings
from remail.utils.session_management import session


def _load_enum[TEnum: Enum](enum_type: type[TEnum], value: str) -> TEnum:
    normalized = value
    if "." in normalized:
        enum_name = normalized.rsplit(".", 1)[-1]
        if enum_name in enum_type.__members__:
            return enum_type[enum_name]
        normalized = enum_name.lower()
    return enum_type(normalized)


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
    ollama_base_url: str
    selected_local_model: str | None

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
            theme_mode=_load_enum(ThemeMode, settings.theme_mode),
            font_size=_load_enum(FontSize, settings.font_size),
            font_family=_load_enum(FontFamily, settings.font_family),
            language=_load_enum(Language, settings.language),
            timezone=_load_enum(Timezone, settings.timezone),
            desktop_notifications=settings.desktop_notifications,
            email_notifications=settings.email_notifications,
            quiet_hours=settings.quiet_hours,
            llm_url=settings.llm_url,
            llm_key=settings.llm_key,
            ollama_base_url=getattr(settings, "ollama_base_url", "http://localhost:11434"),
            selected_local_model=getattr(settings, "selected_local_model", None),
            )
        
        
