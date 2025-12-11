"""Settings service for managing application preferences."""

from sqlmodel import Session, select

from remail.database.db import engine
from remail.models.settings import Settings


class SettingsService:
    """Service for managing application settings."""

    @staticmethod
    def init_settings() -> Settings:
        """
        Initialize settings table and ensure default row exists.

        Creates the settings table if it doesn't exist and inserts a default
        settings row with id=1 if no settings exist yet.

        Returns:
            The settings row (either existing or newly created).
        """
        with Session(engine) as session:
            # Check if settings row with id=1 exists
            statement = select(Settings).where(Settings.id == 1)
            existing = session.exec(statement).first()

            if not existing:
                # Create default settings
                default_settings = Settings(
                    id=1,
                    theme_mode="system",
                    font_size="medium",
                    font_family="system",
                    language="en",
                    timezone="Europe/London",
                    desktop_notifications=True,
                    email_notifications=True,
                    quiet_hours=False,
                )
                session.add(default_settings)
                session.commit()
                session.refresh(default_settings)
                return default_settings

            return existing

    @staticmethod
    def load_settings() -> Settings | None:
        """
        Load settings for id=1.

        Returns:
            Settings object if found, None otherwise.
        """
        with Session(engine) as session:
            statement = select(Settings).where(Settings.id == 1)
            return session.exec(statement).first()

    @staticmethod
    def save_settings(
        theme_mode: str | None = None,
        font_size: str | None = None,
        font_family: str | None = None,
        language: str | None = None,
        timezone: str | None = None,
        desktop_notifications: bool | None = None,
        email_notifications: bool | None = None,
        quiet_hours: bool | None = None,
    ) -> Settings:
        """
        Update settings for id=1.

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
            Updated Settings object
        """
        with Session(engine) as session:
            statement = select(Settings).where(Settings.id == 1)
            settings = session.exec(statement).first()

            if not settings:
                # This shouldn't happen if init_settings was called, but handle it
                settings = Settings(id=1)
                session.add(settings)

            if theme_mode is not None:
                settings.theme_mode = theme_mode
            if font_size is not None:
                settings.font_size = font_size
            if font_family is not None:
                settings.font_family = font_family
            if language is not None:
                settings.language = language
            if timezone is not None:
                settings.timezone = timezone
            if desktop_notifications is not None:
                settings.desktop_notifications = desktop_notifications
            if email_notifications is not None:
                settings.email_notifications = email_notifications
            if quiet_hours is not None:
                settings.quiet_hours = quiet_hours

            session.add(settings)
            session.commit()
            session.refresh(settings)

            return settings
