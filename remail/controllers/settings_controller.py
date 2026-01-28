from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.interfaces.email.services.settings_service import SettingsService


class SettingsController:
    """Controller for application settings operations."""

    def __init__(self):
        """Initialize settings controller."""
        self.service = SettingsService()

    def initialize_settings(self) -> SettingsDTO:
        """
        Initialize settings table and ensure default row exists.

        Returns:
            SettingsDTO with initialized settings
        """

        settings = self.service.init_settings()

        return SettingsDTO.from_model(settings)

    def get_settings(self) -> SettingsDTO | None:
        """
        Load current settings.

        Returns:
            SettingsDTO if found, None otherwise
        """

        settings = self.service.load_settings()

        if not settings:
            return None

        return SettingsDTO.from_model(settings)

    def update_settings(
        self,
        theme_mode: str | None = None,
        font_size: str | None = None,
        font_family: str | None = None,
        language: str | None = None,
        timezone: str | None = None,
        desktop_notifications: bool | None = None,
        email_notifications: bool | None = None,
        quiet_hours: bool | None = None,
    ) -> SettingsDTO:
        """
        Update application settings.

        Args:
            theme_mode: Theme mode (light/dark/system)
            font_size: Font size (small/medium/large)
            font_family: Font family name
            language: Language code
            timezone: Timezone string
            desktop_notifications: Whether desktop notifications are enabled
            email_notifications: Whether email notifications are enabled
            quiet_hours: Whether quiet hours mode is enabled

        Returns:
            Updated SettingsDTO
        """

        settings = self.service.save_settings(
            theme_mode=theme_mode,
            font_size=font_size,
            font_family=font_family,
            language=language,
            timezone=timezone,
            desktop_notifications=desktop_notifications,
            email_notifications=email_notifications,
            quiet_hours=quiet_hours,
        )

        return SettingsDTO.from_model(settings)
