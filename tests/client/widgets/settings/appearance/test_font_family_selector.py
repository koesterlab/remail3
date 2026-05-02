"""Unit tests for font_family_selector widget."""

from unittest.mock import Mock

import flet as ft
from remail.client.state.app_state import AppState
from remail.client.widgets.settings.appearance.font_family_selector import (
    create_font_family_selector,
)

from remail.enums import FontFamily


class TestCreateFontFamilySelector:
    """Test suite for create_font_family_selector function."""

    def test_returns_column(self):
        """Test that create_font_family_selector returns a Column."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)

        assert isinstance(result, ft.Column)

    def test_has_font_family_label(self):
        """Test that selector has a 'Font family' label."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)

        assert isinstance(result.controls[0], ft.Text)
        assert result.controls[0].value == "Font family"
        assert result.controls[0].weight == ft.FontWeight.BOLD

    def test_has_dropdown(self):
        """Test that selector contains a Dropdown."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)

        assert isinstance(result.controls[1], ft.Dropdown)

    def test_dropdown_has_seven_options(self):
        """Test that Dropdown has all 7 font family options."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)
        dropdown = result.controls[1]

        assert len(dropdown.options) == 7

    def test_dropdown_contains_all_font_families(self):
        """Test that dropdown contains all FontFamily enum values."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)
        dropdown = result.controls[1]

        option_keys = [opt.key for opt in dropdown.options]
        assert FontFamily.ARIAL.value in option_keys
        assert FontFamily.ROBOTO.value in option_keys
        assert FontFamily.GEORGIA.value in option_keys
        assert FontFamily.COURIER_NEW.value in option_keys
        assert FontFamily.TIMES_NEW_ROMAN.value in option_keys
        assert FontFamily.VERDANA.value in option_keys
        assert FontFamily.TAHOMA.value in option_keys

    def test_default_value_from_app_state(self):
        """Test that Dropdown default value comes from app_state."""
        page = Mock(spec=ft.Page)
        app_state = AppState(font_family=FontFamily.ROBOTO)

        result = create_font_family_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.value == FontFamily.ROBOTO.value

    def test_arial_font_selected_by_default(self):
        """Test that ARIAL font is selected when app_state has default."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.value == FontFamily.ARIAL.value

    def test_dropdown_has_on_change_handler(self):
        """Test that Dropdown has an on_change event handler."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.on_change is not None
        assert callable(dropdown.on_change)

    def test_dropdown_width(self):
        """Test that Dropdown has correct width."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)
        dropdown = result.controls[1]

        assert dropdown.width == 200

    def test_column_spacing(self):
        """Test that Column has correct spacing."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_font_family_selector(page, app_state)

        assert result.spacing == 10

    def test_multiple_instances_independent(self):
        """Test that multiple selector instances are independent."""
        page = Mock(spec=ft.Page)
        app_state1 = AppState(font_family=FontFamily.GEORGIA)
        app_state2 = AppState(font_family=FontFamily.VERDANA)

        selector1 = create_font_family_selector(page, app_state1)
        selector2 = create_font_family_selector(page, app_state2)

        assert selector1.controls[1].value == FontFamily.GEORGIA.value
        assert selector2.controls[1].value == FontFamily.VERDANA.value
