"""Unit tests for SettingsService."""

from sqlmodel import Session

from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone
from remail.interfaces.email.services.settings_service import SettingsService
from remail.models.settings import Settings


class TestSettingsService:
    """Test suite for SettingsService."""

    def test_load_settings_creates_default_when_none_exist(self, test_engine):
        """Test that load_settings creates default settings when none exist."""
        service = SettingsService()
        result = service.load_settings()

        assert result is not None
        assert result.id == 1
        assert result.theme_mode == "system"
        assert result.font_size == "medium"
        assert result.font_family == "system"
        assert result.language == "en"
        assert result.timezone == "Europe/London"
        assert result.desktop_notifications is True
        assert result.email_notifications is True
        assert result.quiet_hours is False

    def test_load_settings_returns_existing_settings(self, test_engine):
        """Test that load_settings returns existing settings without creating new ones."""
        # Create existing settings
        with Session(test_engine) as session:
            existing = Settings(
                id=1,
                theme_mode=ThemeMode.DARK.value,
                font_size=FontSize.LARGE.value,
                font_family=FontFamily.ROBOTO.value,
                language=Language.GERMAN.value,
                timezone=Timezone.EUROPE_BERLIN.value,
                desktop_notifications=False,
                email_notifications=False,
                quiet_hours=True,
            )
            session.add(existing)
            session.commit()

        service = SettingsService()
        result = service.load_settings()

        assert result.id == 1
        assert result.theme_mode == ThemeMode.DARK.value
        assert result.font_size == FontSize.LARGE.value
        assert result.font_family == FontFamily.ROBOTO.value
        assert result.language == Language.GERMAN.value
        assert result.timezone == Timezone.EUROPE_BERLIN.value
        assert result.desktop_notifications is False
        assert result.email_notifications is False
        assert result.quiet_hours is True

    def test_save_settings_updates_all_fields(self, test_engine):
        """Test that save_settings updates all fields."""
        # Create initial settings
        service = SettingsService()
        service.load_settings()  # Initialize with defaults

        # Update settings
        new_settings = Settings(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.LARGE.value,
            font_family=FontFamily.ROBOTO.value,
            language=Language.GERMAN.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=False,
            email_notifications=False,
            quiet_hours=True,
        )
        service.save_settings(new_settings)

        # Verify settings were updated
        result = service.load_settings()
        assert result.theme_mode == ThemeMode.DARK.value
        assert result.font_size == FontSize.LARGE.value
        assert result.font_family == FontFamily.ROBOTO.value
        assert result.language == Language.GERMAN.value
        assert result.timezone == Timezone.EUROPE_BERLIN.value
        assert result.desktop_notifications is False
        assert result.email_notifications is False
        assert result.quiet_hours is True

    def test_save_settings_creates_if_not_exists(self, test_engine):
        """Test that save_settings creates settings if they don't exist."""
        service = SettingsService()

        new_settings = Settings(
            id=1,
            theme_mode=ThemeMode.LIGHT.value,
            font_size=FontSize.SMALL.value,
            font_family=FontFamily.COURIER_NEW.value,
            language=Language.FRENCH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=False,
            quiet_hours=True,
        )
        service.save_settings(new_settings)

        # Verify settings were created
        result = service.load_settings()
        assert result is not None
        assert result.id == 1
        assert result.theme_mode == ThemeMode.LIGHT.value
        assert result.font_size == FontSize.SMALL.value

    def test_save_settings_preserves_id(self, test_engine):
        """Test that save_settings always uses id=1."""
        service = SettingsService()
        service.load_settings()

        # Try to save with different id (should be overridden to 1)
        new_settings = Settings(
            id=999,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )
        service.save_settings(new_settings)

        result = service.load_settings()
        assert result.id == 1  # Should always be 1

    def test_notification_settings_persist(self, test_engine):
        """Test that notification settings persist correctly."""
        service = SettingsService()

        # Create and save settings with specific notification values
        settings = Settings(
            id=1,
            theme_mode=ThemeMode.SYSTEM.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=False,
            email_notifications=False,
            quiet_hours=True,
        )
        service.save_settings(settings)

        # Load and verify
        loaded = service.load_settings()
        assert loaded.desktop_notifications is False
        assert loaded.email_notifications is False
        assert loaded.quiet_hours is True

    def test_multiple_save_updates_same_record(self, test_engine):
        """Test that multiple saves update the same record."""
        service = SettingsService()

        # First save
        settings1 = Settings(
            id=1,
            theme_mode=ThemeMode.LIGHT.value,
            font_size=FontSize.SMALL.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )
        service.save_settings(settings1)

        # Second save
        settings2 = Settings(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.LARGE.value,
            font_family=FontFamily.ROBOTO.value,
            language=Language.GERMAN.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=False,
            email_notifications=False,
            quiet_hours=True,
        )
        service.save_settings(settings2)

        # Verify only one record exists with updated values
        result = service.load_settings()
        assert result.theme_mode == ThemeMode.DARK.value
        assert result.font_size == FontSize.LARGE.value

        # Verify no duplicate records
        with Session(test_engine) as session:
            from sqlmodel import select
            all_settings = session.exec(select(Settings)).all()
            assert len(all_settings) == 1
