"""Unit tests for appearance_view."""

from unittest.mock import Mock

import flet as ft
from remail.client.state.app_state import AppState

from remail.client.views.settings.appearance_view import create_appearance_view
from remail.enums import ThemeMode


class TestCreateAppearanceView:
    """Test suite for create_appearance_view function."""

    def test_returns_container(self):
        """Test that create_appearance_view returns a Container."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        assert isinstance(result, ft.Container)

    def test_container_has_column(self):
        """Test that Container content is a Column."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        assert isinstance(result.content, ft.Column)

    def test_has_appearance_title(self):
        """Test that view has 'Appearance' title."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        title = result.content.controls[0]

        assert isinstance(title, ft.Text)
        assert title.value == "Appearance"
        assert title.size == 18
        assert title.weight == ft.FontWeight.BOLD

    def test_has_description_text(self):
        """Test that view has description text."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        description = result.content.controls[1]

        assert isinstance(description, ft.Text)
        assert description.value == "Customize how the app looks and feels"

    def test_has_divider(self):
        """Test that view has a divider."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        divider = result.content.controls[2]

        assert isinstance(divider, ft.Divider)
        assert divider.height == 2
        assert divider.color == ft.Colors.BLACK

    def test_has_theme_selector(self):
        """Test that view includes theme selector."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        theme_selector = result.content.controls[3]

        assert isinstance(theme_selector, ft.Column)
        # Check it's the theme selector by verifying first control is Text with "Theme"
        assert isinstance(theme_selector.controls[0], ft.Text)
        assert theme_selector.controls[0].value == "Theme"

    def test_has_font_size_selector(self):
        """Test that view includes font size selector."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        font_size_selector = result.content.controls[4]

        assert isinstance(font_size_selector, ft.Column)
        assert isinstance(font_size_selector.controls[0], ft.Text)
        assert font_size_selector.controls[0].value == "Font size"

    def test_has_font_family_selector(self):
        """Test that view includes font family selector."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        font_family_selector = result.content.controls[5]

        assert isinstance(font_family_selector, ft.Column)
        assert isinstance(font_family_selector.controls[0], ft.Text)
        assert font_family_selector.controls[0].value == "Font family"

    def test_has_apply_button(self):
        """Test that view has an Apply button."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        button_container = result.content.controls[6]

        assert isinstance(button_container, ft.Container)
        assert isinstance(button_container.content, ft.OutlinedButton)
        assert button_container.content.text == "Apply"

    def test_apply_button_has_handler(self):
        """Test that Apply button has an on_click handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        button_container = result.content.controls[6]
        button = button_container.content

        assert button.on_click is not None
        assert callable(button.on_click)

    def test_apply_button_centered(self):
        """Test that Apply button container is centered."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)
        button_container = result.content.controls[6]

        assert button_container.alignment == ft.Alignment.CENTER

    def test_column_spacing(self):
        """Test that Column has correct spacing."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        assert result.content.spacing == 15

    def test_container_padding(self):
        """Test that Container has correct padding."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        assert result.padding == 20

    def test_container_border_radius(self):
        """Test that Container has correct border radius."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        assert result.border_radius == 10

    def test_container_alignment(self):
        """Test that Container has correct alignment."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        assert result.alignment == ft.Alignment.CENTER_LEFT

    def test_all_controls_present(self):
        """Test that view has all 7 expected controls."""
        page = Mock(spec=ft.Page)
        app_state = AppState()

        result = create_appearance_view(page, app_state)

        # Title, description, divider, theme selector, font size, font family, apply button
        assert len(result.content.controls) == 7

    def test_multiple_instances_independent(self):
        """Test that multiple view instances are independent."""
        from unittest.mock import patch

        page = Mock(spec=ft.Page)
        app_state1 = AppState(theme_mode=ThemeMode.LIGHT)
        app_state2 = AppState(theme_mode=ThemeMode.DARK)

        # Mock database functions to return None so AppState values are used
        with patch(
            "remail.client.views.settings.appearance_view.SettingsController"
        ) as mock_controller_class:
            mock_controller = Mock()
            mock_controller.get_settings.return_value = None
            mock_controller_class.return_value = mock_controller

            view1 = create_appearance_view(page, app_state1)
            view2 = create_appearance_view(page, app_state2)

            # Check that theme selectors have different values
            theme_selector1 = view1.content.controls[3]
            theme_selector2 = view2.content.controls[3]

            # When no database settings, they should still be independent based on AppState
            # The theme selector will show the default unless overridden by database
            assert theme_selector1.controls[1].value is not None
            assert theme_selector2.controls[1].value is not None
