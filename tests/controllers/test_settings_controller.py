"""Unit tests for SettingsController."""

from unittest.mock import Mock, patch

from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.controllers.settings_controller import SettingsController
from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone


class TestSettingsController:
    """Test suite for SettingsController."""

    def test_initialize_settings_creates_default_settings(self):
        """Test that initialize_settings creates default settings."""
        with patch("remail.controllers.settings_controller.SettingsService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            controller = SettingsController()
            controller.initialize_settings()

            mock_service.init_settings.assert_called_once()

    def test_get_settings_returns_none_when_no_settings(self):
        """Test that get_settings returns None when no settings exist."""
        with patch("remail.controllers.settings_controller.SettingsService") as mock_service_class:
            mock_service = Mock()
            mock_service.load_settings.return_value = None
            mock_service_class.return_value = mock_service

            controller = SettingsController()
            result = controller.get_settings()

            assert result is None
            mock_service.load_settings.assert_called_once()

    def test_get_settings_returns_dto_when_settings_exist(self):
        """Test that get_settings returns SettingsDTO when settings exist."""
        with patch("remail.controllers.settings_controller.SettingsService") as mock_service_class:
            mock_service = Mock()
            mock_settings = Mock()
            mock_settings.id = 1
            mock_settings.theme_mode = ThemeMode.DARK.value
            mock_settings.font_size = FontSize.LARGE.value
            mock_settings.font_family = FontFamily.ROBOTO.value
            mock_settings.language = Language.GERMAN.value
            mock_settings.timezone = Timezone.EUROPE_BERLIN.value
            mock_settings.desktop_notifications = True
            mock_settings.email_notifications = False
            mock_settings.quiet_hours = True
            mock_service.load_settings.return_value = mock_settings
            mock_service_class.return_value = mock_service

            controller = SettingsController()
            result = controller.get_settings()

            assert isinstance(result, SettingsDTO)
            assert result.theme_mode == ThemeMode.DARK.value
            assert result.font_size == FontSize.LARGE.value
            assert result.font_family == FontFamily.ROBOTO.value
            assert result.language == Language.GERMAN.value
            assert result.timezone == Timezone.EUROPE_BERLIN.value
            assert result.desktop_notifications is True
            assert result.email_notifications is False
            assert result.quiet_hours is True

    def test_update_settings_with_all_parameters(self):
        """Test that update_settings works with all parameters."""
        with patch("remail.controllers.settings_controller.SettingsService") as mock_service_class:
            mock_service = Mock()
            mock_updated_settings = Mock()
            mock_updated_settings.id = 1
            mock_updated_settings.theme_mode = ThemeMode.LIGHT.value
            mock_updated_settings.font_size = FontSize.SMALL.value
            mock_updated_settings.font_family = FontFamily.COURIER_NEW.value
            mock_updated_settings.language = Language.FRENCH.value
            mock_updated_settings.timezone = Timezone.AMERICA_NEW_YORK.value
            mock_updated_settings.desktop_notifications = False
            mock_updated_settings.email_notifications = True
            mock_updated_settings.quiet_hours = False
            mock_service.save_settings.return_value = mock_updated_settings
            mock_service_class.return_value = mock_service

            controller = SettingsController()
            result = controller.update_settings(
                theme_mode=ThemeMode.LIGHT.value,
                font_size=FontSize.SMALL.value,
                font_family=FontFamily.COURIER_NEW.value,
                language=Language.FRENCH.value,
                timezone=Timezone.AMERICA_NEW_YORK.value,
                desktop_notifications=False,
                email_notifications=True,
                quiet_hours=False,
            )

            assert isinstance(result, SettingsDTO)
            assert result.theme_mode == ThemeMode.LIGHT.value
            assert result.font_size == FontSize.SMALL.value
            assert result.font_family == FontFamily.COURIER_NEW.value
            assert result.language == Language.FRENCH.value
            assert result.timezone == Timezone.AMERICA_NEW_YORK.value
            assert result.desktop_notifications is False
            assert result.email_notifications is True
            assert result.quiet_hours is False

            mock_service.save_settings.assert_called_once_with(
                theme_mode=ThemeMode.LIGHT.value,
                font_size=FontSize.SMALL.value,
                font_family=FontFamily.COURIER_NEW.value,
                language=Language.FRENCH.value,
                timezone=Timezone.AMERICA_NEW_YORK.value,
                desktop_notifications=False,
                email_notifications=True,
                quiet_hours=False,
            )

    def test_update_settings_with_partial_parameters(self):
        """Test that update_settings works with only some parameters."""
        with patch("remail.controllers.settings_controller.SettingsService") as mock_service_class:
            mock_service = Mock()
            mock_updated_settings = Mock()
            mock_updated_settings.id = 1
            mock_updated_settings.theme_mode = ThemeMode.DARK.value
            mock_updated_settings.font_size = FontSize.MEDIUM.value
            mock_updated_settings.font_family = FontFamily.ARIAL.value
            mock_updated_settings.language = Language.ENGLISH.value
            mock_updated_settings.timezone = Timezone.EUROPE_LONDON.value
            mock_updated_settings.desktop_notifications = True
            mock_updated_settings.email_notifications = True
            mock_updated_settings.quiet_hours = False
            mock_service.save_settings.return_value = mock_updated_settings
            mock_service_class.return_value = mock_service

            controller = SettingsController()
            result = controller.update_settings(
                theme_mode=ThemeMode.DARK.value,
                desktop_notifications=True,
            )

            assert isinstance(result, SettingsDTO)
            mock_service.save_settings.assert_called_once_with(
                theme_mode=ThemeMode.DARK.value,
                font_size=None,
                font_family=None,
                language=None,
                timezone=None,
                desktop_notifications=True,
                email_notifications=None,
                quiet_hours=None,
            )

    def test_update_settings_returns_dto(self):
        """Test that update_settings always returns a SettingsDTO."""
        with patch("remail.controllers.settings_controller.SettingsService") as mock_service_class:
            mock_service = Mock()
            mock_updated_settings = Mock()
            mock_updated_settings.id = 1
            mock_updated_settings.theme_mode = ThemeMode.SYSTEM.value
            mock_updated_settings.font_size = FontSize.MEDIUM.value
            mock_updated_settings.font_family = FontFamily.ARIAL.value
            mock_updated_settings.language = Language.ENGLISH.value
            mock_updated_settings.timezone = Timezone.EUROPE_LONDON.value
            mock_updated_settings.desktop_notifications = True
            mock_updated_settings.email_notifications = True
            mock_updated_settings.quiet_hours = False
            mock_service.save_settings.return_value = mock_updated_settings
            mock_service_class.return_value = mock_service

            controller = SettingsController()
            result = controller.update_settings()

            assert isinstance(result, SettingsDTO)
            assert not isinstance(result, dict)
