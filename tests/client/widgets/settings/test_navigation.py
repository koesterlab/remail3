"""Unit tests for settings navigation widget."""

from unittest.mock import Mock

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.settings.navigation import create_settings_navigation
from remail.enums import MainView, SettingsSubView


class TestCreateSettingsNavigation:
    """Test suite for create_settings_navigation function."""

    def test_returns_container(self):
        """Test that create_settings_navigation returns a Container."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        assert isinstance(result, ft.Container)

    def test_container_has_column(self):
        """Test that Container content is a Column."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        assert isinstance(result.content, ft.Column)

    def test_has_settings_title(self):
        """Test that navigation has 'Settings' title."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        title = result.content.controls[0]

        assert isinstance(title, ft.Text)
        assert title.value == "Settings"
        assert title.size == 24
        assert title.weight == ft.FontWeight.BOLD

    def test_has_divider(self):
        """Test that navigation has a divider."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        divider = result.content.controls[1]

        assert isinstance(divider, ft.Divider)
        assert divider.height == 2

    def test_has_four_navigation_buttons(self):
        """Test that navigation has 4 menu items."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        # Title + Divider + 4 buttons = 6 controls
        assert len(result.content.controls) == 6

    def test_navigation_button_labels(self):
        """Test that navigation buttons have correct labels."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        buttons = result.content.controls[2:]  # Skip title and divider

        assert buttons[0].text == "Appearance"
        assert buttons[1].text == "Email Accounts"
        assert buttons[2].text == "Language & Region"
        assert buttons[3].text == "Notifications"

    def test_all_buttons_are_text_buttons(self):
        """Test that all navigation items are TextButtons."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        buttons = result.content.controls[2:]

        assert all(isinstance(btn, ft.TextButton) for btn in buttons)

    def test_buttons_have_click_handlers(self):
        """Test that all navigation buttons have on_click handlers."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        buttons = result.content.controls[2:]

        for button in buttons:
            assert button.on_click is not None
            assert callable(button.on_click)

    def test_container_width(self):
        """Test that Container has correct width."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        assert result.width == 200

    def test_container_padding(self):
        """Test that Container has correct padding."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        assert result.padding == 10

    def test_column_spacing(self):
        """Test that Column has correct spacing."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        assert result.content.spacing == 16

    def test_active_state_when_appearance_selected(self):
        """Test that Appearance button is highlighted when active."""
        app_state = AppState()
        app_state.set_current_view(MainView.SETTINGS, SettingsSubView.APPEARANCE)
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        appearance_button = result.content.controls[2]

        # Active button should have PRIMARY color
        assert appearance_button.style.color == ft.Colors.PRIMARY
        assert appearance_button.style.bgcolor == ft.Colors.PRIMARY_CONTAINER

    def test_inactive_state_for_non_selected_buttons(self):
        """Test that non-selected buttons are not highlighted."""
        app_state = AppState()
        app_state.set_current_view(MainView.SETTINGS, SettingsSubView.APPEARANCE)
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        email_button = result.content.controls[3]

        # Inactive button should have ON_SURFACE color and no bgcolor
        assert email_button.style.color == ft.Colors.ON_SURFACE
        assert email_button.style.bgcolor is None

    def test_multiple_instances_independent(self):
        """Test that multiple navigation instances are independent."""
        app_state1 = AppState()
        app_state2 = AppState()
        app_state1.set_current_view(MainView.SETTINGS, SettingsSubView.APPEARANCE)
        app_state2.set_current_view(MainView.SETTINGS, SettingsSubView.LANGUAGE)
        on_navigate = Mock()

        nav1 = create_settings_navigation(app_state1, on_navigate)
        nav2 = create_settings_navigation(app_state2, on_navigate)

        # Check that different buttons are active in each instance
        appearance_btn1 = nav1.content.controls[2]
        language_btn2 = nav2.content.controls[4]

        assert appearance_btn1.style.color == ft.Colors.PRIMARY
        assert language_btn2.style.color == ft.Colors.PRIMARY
