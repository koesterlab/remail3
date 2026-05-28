from enum import Enum

from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.interfaces.email.services.settings_service import SettingsService
from remail.utils.session_management import session


def _settings_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


class SettingsController:
    """Controller for application settings operations."""

    def __init__(self):
        """Initialize settings controller."""
        self.service = SettingsService()

    @session
    def get_settings(self) -> SettingsDTO:
        """
        Load current settings.

        Returns:
            SettingsDTO
        """
        return SettingsDTO.from_model(self.service.load_settings())  # type:ignore

    @session
    def update_settings(
        self,
        settings: SettingsDTO,
    ) -> None:
        """
        Update application settings.

        Args:
            settings: SettingsDTO with updated values

        Returns:
            Updated SettingsDTO
        """

        settings_obj = self.service.load_settings()

        settings_obj.theme_mode = _settings_value(settings.theme_mode)
        settings_obj.font_size = _settings_value(settings.font_size)
        settings_obj.font_family = _settings_value(settings.font_family)
        settings_obj.language = _settings_value(settings.language)
        settings_obj.timezone = _settings_value(settings.timezone)
        settings_obj.desktop_notifications = settings.desktop_notifications
        settings_obj.email_notifications = settings.email_notifications
        settings_obj.quiet_hours = settings.quiet_hours
