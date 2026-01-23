"""Unit tests for SettingsService."""

from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone
from remail.interfaces.email.services.settings_service import SettingsService
from remail.models.settings import Settings


class TestSettingsService:
    """Test suite for SettingsService."""

    def test_init_settings_creates_default_settings(self, test_session):
        """Test that init_settings creates default settings when none exist."""
        result = SettingsService.init_settings()

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

    def test_init_settings_returns_existing_settings(self, test_session):
        """Test that init_settings returns existing settings without overwriting."""
        # Create existing settings
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
        test_session.add(existing)
        test_session.commit()

        result = SettingsService.init_settings()

        assert result.id == 1
        assert result.theme_mode == ThemeMode.DARK.value
        assert result.font_size == FontSize.LARGE.value
        assert result.font_family == FontFamily.ROBOTO.value
        assert result.language == Language.GERMAN.value
        assert result.timezone == Timezone.EUROPE_BERLIN.value
        assert result.desktop_notifications is False
        assert result.email_notifications is False
        assert result.quiet_hours is True

    def test_load_settings_returns_none_when_no_settings(self, test_session):
        """Test that load_settings returns None when no settings exist."""
        result = SettingsService.load_settings()

        assert result is None

    def test_load_settings_returns_settings_when_exist(self, test_session):
        """Test that load_settings returns settings when they exist."""
        # Create settings
        settings = Settings(
            id=1,
            theme_mode=ThemeMode.LIGHT.value,
            font_size=FontSize.SMALL.value,
            font_family=FontFamily.COURIER_NEW.value,
            language=Language.FRENCH.value,
            timezone=Timezone.AMERICA_NEW_YORK.value,
            desktop_notifications=True,
            email_notifications=False,
            quiet_hours=True,
        )
        test_session.add(settings)
        test_session.commit()

        result = SettingsService.load_settings()

        assert result is not None
        assert result.theme_mode == ThemeMode.LIGHT.value
        assert result.font_size == FontSize.SMALL.value
        assert result.font_family == FontFamily.COURIER_NEW.value
        assert result.language == Language.FRENCH.value
        assert result.timezone == Timezone.AMERICA_NEW_YORK.value
        assert result.desktop_notifications is True
        assert result.email_notifications is False
        assert result.quiet_hours is True

    def test_save_settings_updates_all_fields(self, test_session):
        """Test that save_settings updates all fields."""
        # Create initial settings
        settings = Settings(
            id=1,
            theme_mode=ThemeMode.SYSTEM.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_LONDON.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )
        test_session.add(settings)
        test_session.commit()

        result = SettingsService.save_settings(
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.LARGE.value,
            font_family=FontFamily.ROBOTO.value,
            language=Language.GERMAN.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=False,
            email_notifications=False,
            quiet_hours=True,
        )

        assert result.theme_mode == ThemeMode.DARK.value
        assert result.font_size == FontSize.LARGE.value
        assert result.font_family == FontFamily.ROBOTO.value
        assert result.language == Language.GERMAN.value
        assert result.timezone == Timezone.EUROPE_BERLIN.value
        assert result.desktop_notifications is False
        assert result.email_notifications is False
        assert result.quiet_hours is True

    def test_save_settings_updates_partial_fields(self, test_session):
        """Test that save_settings only updates provided fields."""
        # Create initial settings
        settings = Settings(
            id=1,
            theme_mode=ThemeMode.SYSTEM.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_LONDON.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )
        test_session.add(settings)
        test_session.commit()

        result = SettingsService.save_settings(
            theme_mode=ThemeMode.DARK.value,
            desktop_notifications=False,
        )

        # Updated fields
        assert result.theme_mode == ThemeMode.DARK.value
        assert result.desktop_notifications is False

        # Unchanged fields
        assert result.font_size == FontSize.MEDIUM.value
        assert result.font_family == FontFamily.ARIAL.value
        assert result.language == Language.ENGLISH.value
        assert result.timezone == Timezone.EUROPE_LONDON.value
        assert result.email_notifications is True
        assert result.quiet_hours is False

    def test_save_settings_creates_if_not_exists(self, test_session):
        """Test that save_settings creates settings if they don't exist."""
        result = SettingsService.save_settings(
            theme_mode=ThemeMode.LIGHT.value,
            font_size=FontSize.SMALL.value,
        )

        assert result is not None
        assert result.id == 1
        assert result.theme_mode == ThemeMode.LIGHT.value
        assert result.font_size == FontSize.SMALL.value

    def test_save_settings_preserves_id(self, test_session):
        """Test that save_settings preserves the id=1."""
        # Create initial settings
        settings = Settings(id=1, theme_mode=ThemeMode.SYSTEM.value)
        test_session.add(settings)
        test_session.commit()

        result = SettingsService.save_settings(theme_mode=ThemeMode.DARK.value)

        assert result.id == 1

    def test_notification_settings_persist(self, test_session):
        """Test that notification settings persist correctly."""
        # Create and save settings
        SettingsService.init_settings()
        SettingsService.save_settings(
            desktop_notifications=False,
            email_notifications=False,
            quiet_hours=True,
        )

        # Load and verify
        loaded = SettingsService.load_settings()
        assert loaded.desktop_notifications is False
        assert loaded.email_notifications is False
        assert loaded.quiet_hours is True
