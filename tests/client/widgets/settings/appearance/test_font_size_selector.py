"""Unit tests for font_size_selector widget."""

from unittest.mock import Mock

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.settings.appearance.font_size_selector import create_font_size_selector
from remail.enums import FontSize


class TestCreateFontSizeSelector:
    """Test suite for create_font_size_selector function."""

    def test_returns_column(self):
        """Test that create_font_size_selector returns a Column."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)

        assert isinstance(result, ft.Column)

    def test_has_font_size_label(self):
        """Test that selector has a 'Font size' label."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)

        assert isinstance(result.controls[0], ft.Text)
        assert result.controls[0].value == "Font size"
        assert result.controls[0].weight == ft.FontWeight.BOLD

    def test_has_dropdown(self):
        """Test that selector contains a Dropdown."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)

        assert isinstance(result.controls[1], ft.Dropdown)

    def test_dropdown_has_three_options(self):
        """Test that Dropdown has SMALL, MEDIUM, and LARGE options."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)
        dropdown = result.controls[1]

        assert len(dropdown.options) == 3

    def test_dropdown_option_values(self):
        """Test that dropdown options have correct values."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)
        dropdown = result.controls[1]

        option_keys = [opt.key for opt in dropdown.options]
        assert FontSize.SMALL.value in option_keys
        assert FontSize.MEDIUM.value in option_keys
        assert FontSize.LARGE.value in option_keys

    def test_default_value_from_app_state(self):
        """Test that Dropdown default value comes from app_state."""
        page = Mock(spec=ft.Page)
        app_state = AppState(font_size=FontSize.LARGE)

        result = create_font_size_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.value == FontSize.LARGE.value

    def test_medium_font_selected_by_default(self):
        """Test that MEDIUM font is selected when app_state has default."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.value == FontSize.MEDIUM.value

    def test_dropdown_has_on_change_handler(self):
        """Test that Dropdown has an on_change event handler."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.on_change is not None
        assert callable(dropdown.on_change)

    def test_dropdown_width(self):
        """Test that Dropdown has correct width."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.width == 200

    def test_column_spacing(self):
        """Test that Column has correct spacing."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_size_selector(page, app_state)

        assert result.spacing == 10

    def test_multiple_instances_independent(self):
        """Test that multiple selector instances are independent."""
        page = Mock(spec=ft.Page)
        app_state1 = AppState(font_size=FontSize.SMALL)
        app_state2 = AppState(font_size=FontSize.LARGE)

        selector1 = create_font_size_selector(page, app_state1)
        selector2 = create_font_size_selector(page, app_state2)

        assert selector1.controls[1].value == FontSize.SMALL.value
        assert selector2.controls[1].value == FontSize.LARGE.value
