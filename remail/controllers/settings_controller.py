from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.interfaces.email.services.settings_service import SettingsService
from remail.models import Settings


class SettingsController:
    """Controller for application settings operations."""

    def __init__(self):
        """Initialize settings controller."""
        self.service = SettingsService()

    def get_settings(self) -> SettingsDTO | None:
        """
        Load current settings.

        Returns:
            SettingsDTO
        """
        return SettingsDTO.from_model(self.service.load_settings())

    def update_settings(
            self,
            settings: SettingsDTO,
    ) -> SettingsDTO:
        """
        Update application settings.

        Args:
            settings: SettingsDTO with updated values

        Returns:
            Updated SettingsDTO
        """
        db_obj = Settings(
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
        return SettingsDTO.from_model(self.service.save_settings(db_obj))