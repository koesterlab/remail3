"""Unit tests for theme_selector widget."""

from unittest.mock import Mock

import flet as ft
from remail.client.state.app_state import AppState
from remail.client.widgets.settings.appearance.theme_selector import create_theme_selector

from remail.enums import ThemeMode


class TestCreateThemeSelector:
    """Test suite for create_theme_selector function."""

    def test_returns_column(self):
        """Test that create_theme_selector returns a Column."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)

        assert isinstance(result, ft.Column)

    def test_has_theme_label(self):
        """Test that selector has a 'Theme' label."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)

        assert isinstance(result.controls[0], ft.Text)
        assert result.controls[0].value == "Theme"
        assert result.controls[0].weight == ft.FontWeight.BOLD

    def test_has_radio_group(self):
        """Test that selector contains a RadioGroup."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)

        assert isinstance(result.controls[1], ft.RadioGroup)

    def test_radio_group_has_three_options(self):
        """Test that RadioGroup has Light, Dark, and System options."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)
        radio_group = result.controls[1]
        radio_row = radio_group.content

        assert isinstance(radio_row, ft.Row)
        assert len(radio_row.controls) == 3

    def test_radio_options_values(self):
        """Test that radio options have correct values."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)
        radio_group = result.controls[1]
        radio_buttons = radio_group.content.controls

        assert radio_buttons[0].value == ThemeMode.LIGHT.value
        assert radio_buttons[1].value == ThemeMode.DARK.value
        assert radio_buttons[2].value == ThemeMode.SYSTEM.value

    def test_radio_options_labels(self):
        """Test that radio options have correct labels."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)
        radio_group = result.controls[1]
        radio_buttons = radio_group.content.controls

        assert radio_buttons[0].label == "Light"
        assert radio_buttons[1].label == "Dark"
        assert radio_buttons[2].label == "System"

    def test_default_value_from_app_state(self):
        """Test that RadioGroup default value comes from app_state."""
        page = Mock(spec=ft.Page)
        app_state = AppState(theme_mode=ThemeMode.DARK)

        result = create_theme_selector(page, app_state)
        radio_group = result.controls[1]

        assert radio_group.value == ThemeMode.DARK.value

    def test_system_theme_selected_by_default(self):
        """Test that SYSTEM theme is selected when app_state has default."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)
        radio_group = result.controls[1]

        assert radio_group.value == ThemeMode.SYSTEM.value

    def test_radio_group_has_on_change_handler(self):
        """Test that RadioGroup has an on_change event handler."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)
        radio_group = result.controls[1]

        assert radio_group.on_change is not None
        assert callable(radio_group.on_change)

    def test_column_has_correct_spacing(self):
        """Test that Column has correct spacing."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_theme_selector(page, app_state)

        assert result.spacing == 10

    def test_multiple_instances_independent(self):
        """Test that multiple selector instances are independent."""
        page = Mock(spec=ft.Page)
        app_state1 = AppState(theme_mode=ThemeMode.LIGHT)
        app_state2 = AppState(theme_mode=ThemeMode.DARK)

        selector1 = create_theme_selector(page, app_state1)
        selector2 = create_theme_selector(page, app_state2)

        assert selector1.controls[1].value == ThemeMode.LIGHT.value
        assert selector2.controls[1].value == ThemeMode.DARK.value
