"""Unit tests for settings navigation widget."""

from unittest.mock import Mock

import flet as ft
from remail.client.state import MainAppState as AppState
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

    def test_first_control_is_button(self):
        """Test that first control is a navigation button."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        first_control = result.content.controls[0]

        assert isinstance(first_control, ft.TextButton)
        assert first_control.content.value == "Appearance"

    def test_second_control_is_button(self):
        """Test that second control is a navigation button."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        second_control = result.content.controls[1]

        assert isinstance(second_control, ft.TextButton)
        assert second_control.content.value == "Email Accounts"

    def test_has_four_navigation_buttons(self):
        """Test that navigation has 4 menu items."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)

        # 4 buttons without title and divider
        assert len(result.content.controls) == 4

    def test_navigation_button_labels(self):
        """Test that navigation buttons have correct labels."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        buttons = result.content.controls  # All controls are buttons now

        assert buttons[0].content.value == "Appearance"
        assert buttons[1].content.value == "Email Accounts"
        assert buttons[2].content.value == "Language & Region"
        assert buttons[3].content.value == "Notifications"

    def test_all_buttons_are_text_buttons(self):
        """Test that all navigation items are TextButtons."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        buttons = result.content.controls  # All controls are buttons now

        assert all(isinstance(btn, ft.TextButton) for btn in buttons)

    def test_buttons_have_click_handlers(self):
        """Test that all navigation buttons have on_click handlers."""
        app_state = AppState()
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        buttons = result.content.controls  # All controls are buttons now

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
        appearance_button = result.content.controls[0]  # First button is Appearance

        # Active button should have PRIMARY color
        assert appearance_button.style.color == ft.Colors.PRIMARY
        assert appearance_button.style.bgcolor == ft.Colors.PRIMARY_CONTAINER

    def test_inactive_state_for_non_selected_buttons(self):
        """Test that non-selected buttons are not highlighted."""
        app_state = AppState()
        app_state.set_current_view(MainView.SETTINGS, SettingsSubView.APPEARANCE)
        on_navigate = Mock()

        result = create_settings_navigation(app_state, on_navigate)
        email_button = result.content.controls[1]  # Second button is Email Accounts

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
        appearance_btn1 = nav1.content.controls[0]  # First button is Appearance
        language_btn2 = nav2.content.controls[2]  # Third button is Language & Region

        assert appearance_btn1.style.color == ft.Colors.PRIMARY
        assert language_btn2.style.color == ft.Colors.PRIMARY
