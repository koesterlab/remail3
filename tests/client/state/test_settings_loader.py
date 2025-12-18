"""Unit tests for settings_loader."""

from unittest.mock import Mock, patch

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.state.settings_loader import load_settings_into_state
from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone


class TestLoadSettingsIntoState:
    """Test suite for load_settings_into_state function."""

    def test_loads_all_settings_into_app_state(self):
        """Test that all settings are loaded into app state."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        mock_dto = SettingsDTO(
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

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = mock_dto
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            assert app_state.theme_mode == ThemeMode.DARK
            assert app_state.font_size == FontSize.LARGE
            assert app_state.font_family == FontFamily.ROBOTO
            assert app_state.language == Language.GERMAN
            assert app_state.timezone == Timezone.EUROPE_BERLIN
            assert app_state.desktop_notifications is False
            assert app_state.email_notifications is False
            assert app_state.quiet_hours is True

    def test_applies_light_theme_to_page(self):
        """Test that light theme is applied to page."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        mock_dto = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.LIGHT.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_LONDON.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = mock_dto
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            assert mock_page.theme_mode == ft.ThemeMode.LIGHT

    def test_applies_dark_theme_to_page(self):
        """Test that dark theme is applied to page."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        mock_dto = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_LONDON.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = mock_dto
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            assert mock_page.theme_mode == ft.ThemeMode.DARK

    def test_applies_system_theme_to_page(self):
        """Test that system theme is applied to page."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        mock_dto = SettingsDTO(
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

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = mock_dto
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            assert mock_page.theme_mode == ft.ThemeMode.SYSTEM

    def test_handles_no_settings_gracefully(self):
        """Test that function handles no settings without error."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        # Store original values
        original_theme = app_state.theme_mode
        original_font_size = app_state.font_size

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            # App state should still have default values
            assert app_state.theme_mode == original_theme
            assert app_state.font_size == original_font_size

            # Theme should still be applied based on default
            assert mock_page.theme_mode == ft.ThemeMode.SYSTEM

    def test_handles_invalid_enum_values_gracefully(self):
        """Test that function handles invalid enum values without crashing."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        mock_dto = SettingsDTO(
            id=1,
            theme_mode="invalid_theme",
            font_size="invalid_size",
            font_family="invalid_family",
            language="invalid_language",
            timezone="invalid_timezone",
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = mock_dto
            mock_controller_class.return_value = mock_controller

            # Should not raise an exception
            load_settings_into_state(app_state, mock_page)

            # Boolean values should still be loaded
            assert app_state.desktop_notifications is True
            assert app_state.email_notifications is True
            assert app_state.quiet_hours is False

    def test_calls_initialize_settings_on_controller(self):
        """Test that initialize_settings is called on controller."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            mock_controller.initialize_settings.assert_called_once()

    def test_loads_notification_settings_correctly(self):
        """Test that notification settings are loaded correctly."""
        mock_page = Mock(spec=ft.Page)
        app_state = AppState()

        mock_dto = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.SYSTEM.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_LONDON.value,
            desktop_notifications=False,
            email_notifications=False,
            quiet_hours=True,
        )

        with patch(
            "remail.client.state.settings_loader.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.initialize_settings.return_value = mock_dto
            mock_controller_class.return_value = mock_controller

            load_settings_into_state(app_state, mock_page)

            assert app_state.desktop_notifications is False
            assert app_state.email_notifications is False
            assert app_state.quiet_hours is True
