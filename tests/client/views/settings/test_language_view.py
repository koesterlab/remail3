"""Unit tests for language_view."""

from unittest.mock import Mock, patch

import flet as ft
from remail.client.state.app_state import AppState

from remail.client.views.settings.language_view import create_language_view
from remail.enums import Language, Timezone


class TestCreateLanguageView:
    """Test suite for create_language_view function."""

    def test_returns_container(self):
        """Test that create_language_view returns a Container."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        assert isinstance(result, ft.Container)

    def test_container_has_column(self):
        """Test that Container content is a Column."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        assert isinstance(result.content, ft.Column)

    def test_has_language_region_title(self):
        """Test that view has 'Language & Region' title."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        title = result.content.controls[0]

        assert isinstance(title, ft.Text)
        assert title.value == "Language & Region"
        assert title.size == 18
        assert title.weight == ft.FontWeight.BOLD

    def test_has_description_text(self):
        """Test that view has description text."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        description = result.content.controls[1]

        assert isinstance(description, ft.Text)
        assert description.value == "Choose your preferred language for the application"

    def test_has_divider(self):
        """Test that view has a divider."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        divider = result.content.controls[2]

        assert isinstance(divider, ft.Divider)
        assert divider.height == 2
        assert divider.color == ft.Colors.BLACK

    def test_has_language_label(self):
        """Test that view has 'Application Language' label."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        label = result.content.controls[3]

        assert isinstance(label, ft.Text)
        assert label.value == "Application Language"
        assert label.weight == ft.FontWeight.BOLD

    def test_has_language_dropdown(self):
        """Test that view has language dropdown."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        dropdown = result.content.controls[4]

        assert isinstance(dropdown, ft.Dropdown)
        assert dropdown.expand is True

    def test_language_dropdown_has_all_languages(self):
        """Test that language dropdown contains all Language enum values."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        dropdown = result.content.controls[4]

        # Should have all 20 languages
        assert len(dropdown.options) == len(Language)

        option_values = [opt.key for opt in dropdown.options]
        for lang in Language:
            assert lang.value in option_values

    def test_language_dropdown_default_value(self):
        """Test that language dropdown has default value from app_state."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(language=Language.GERMAN)

        with patch(
            "remail.client.views.settings.language_view.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.get_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            result = create_language_view(page, app_state)
            dropdown = result.content.controls[4]

            assert dropdown.value == Language.GERMAN.value

    def test_language_dropdown_has_on_change_handler(self):
        """Test that language dropdown has an on_change handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        dropdown = result.content.controls[4]

        assert dropdown.on_change is not None
        assert callable(dropdown.on_change)

    def test_has_timezone_label(self):
        """Test that view has 'Timezone' label."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        label = result.content.controls[5]

        assert isinstance(label, ft.Text)
        assert label.value == "Timezone"
        assert label.weight == ft.FontWeight.BOLD

    def test_has_timezone_dropdown(self):
        """Test that view has timezone dropdown."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        dropdown = result.content.controls[6]

        assert isinstance(dropdown, ft.Dropdown)
        assert dropdown.expand is True

    def test_timezone_dropdown_has_all_timezones(self):
        """Test that timezone dropdown contains all Timezone enum values."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        dropdown = result.content.controls[6]

        # Should have all 11 timezones
        assert len(dropdown.options) == len(Timezone)

        option_values = [opt.key for opt in dropdown.options]
        for tz in Timezone:
            assert tz.value in option_values

    def test_timezone_dropdown_default_value(self):
        """Test that timezone dropdown has default value from app_state."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(timezone=Timezone.EUROPE_BERLIN)

        with patch(
            "remail.client.views.settings.language_view.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.get_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            result = create_language_view(page, app_state)
            dropdown = result.content.controls[6]

            assert dropdown.value == Timezone.EUROPE_BERLIN.value

    def test_timezone_dropdown_has_on_change_handler(self):
        """Test that timezone dropdown has an on_change handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        dropdown = result.content.controls[6]

        assert dropdown.on_change is not None
        assert callable(dropdown.on_change)

    def test_has_apply_button(self):
        """Test that view has an Apply button."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        button_container = result.content.controls[7]

        assert isinstance(button_container, ft.Container)
        assert isinstance(button_container.content, ft.OutlinedButton)
        assert button_container.content.text == "Apply"

    def test_apply_button_has_handler(self):
        """Test that Apply button has an on_click handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        button_container = result.content.controls[7]
        button = button_container.content

        assert button.on_click is not None
        assert callable(button.on_click)

    def test_apply_button_centered(self):
        """Test that Apply button container is centered."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)
        button_container = result.content.controls[7]

        assert button_container.alignment == ft.Alignment.CENTER

    def test_column_spacing(self):
        """Test that Column has correct spacing."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        assert result.content.spacing == 15

    def test_container_padding(self):
        """Test that Container has correct padding."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        assert result.padding == 20

    def test_container_border_radius(self):
        """Test that Container has correct border radius."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        assert result.border_radius == 10

    def test_container_alignment(self):
        """Test that Container has correct alignment."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        assert result.alignment == ft.Alignment.CENTER_LEFT

    def test_all_controls_present(self):
        """Test that view has all 8 expected controls."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_language_view(page, app_state)

        # Title, description, divider, language label, language dropdown,
        # timezone label, timezone dropdown, apply button
        assert len(result.content.controls) == 8

    def test_multiple_instances_independent(self):
        """Test that multiple view instances are independent."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state1 = AppState(language=Language.ENGLISH, timezone=Timezone.EUROPE_BERLIN)
        app_state2 = AppState(language=Language.FRENCH, timezone=Timezone.EUROPE_BERLIN)

        with patch(
            "remail.client.views.settings.language_view.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.get_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            view1 = create_language_view(page, app_state1)
            view2 = create_language_view(page, app_state2)

            # Check that language dropdowns have different values
            lang_dropdown1 = view1.content.controls[4]
            lang_dropdown2 = view2.content.controls[4]

            assert lang_dropdown1.value == Language.ENGLISH.value
            assert lang_dropdown2.value == Language.FRENCH.value

            # Check that timezone dropdowns have different values
            tz_dropdown1 = view1.content.controls[6]
            tz_dropdown2 = view2.content.controls[6]

            assert tz_dropdown1.value == Timezone.EUROPE_BERLIN.value
            assert tz_dropdown2.value == Timezone.EUROPE_BERLIN.value

    def test_english_selected_by_default(self):
        """Test that ENGLISH language is selected when app_state has default."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        with patch(
            "remail.client.views.settings.language_view.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.get_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            result = create_language_view(page, app_state)
            lang_dropdown = result.content.controls[4]

            assert lang_dropdown.value == Language.ENGLISH.value

    def test_europe_berlin_timezone_selected_by_default(self):
        """Test that EUROPE_BERLIN timezone is selected when app_state has default."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        with patch(
            "remail.client.views.settings.language_view.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.get_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            result = create_language_view(page, app_state)
            tz_dropdown = result.content.controls[6]

            assert tz_dropdown.value == Timezone.EUROPE_BERLIN.value
