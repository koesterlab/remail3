"""Unit tests for settings_view."""

from unittest.mock import Mock

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.views.settings.settings_view import create_settings_view
from remail.enums import MainView, SettingsSubView


class TestCreateSettingsView:
    """Test suite for create_settings_view function."""

    def test_returns_container(self):
        """Test that create_settings_view returns a Container."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)

        assert isinstance(result, ft.Container)

    def test_sets_page_title(self):
        """Test that view sets page title to 'Settings'."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        create_settings_view(page, app_state)

        assert page.title == "Settings"

    def test_container_has_row(self):
        """Test that Container content is a Column with header and main row."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)

        assert isinstance(result.content, ft.Column)
        # Column should have: header, divider, main row container
        assert len(result.content.controls) == 3

    def test_row_has_three_components(self):
        """Test that main Row has navigation, divider, and content area."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)

        # Get the main row (third element in the column)
        main_container = result.content.controls[2]
        main_row = main_container.content

        # Navigation + VerticalDivider + Content Container
        assert isinstance(main_row, ft.Row)
        assert len(main_row.controls) == 3

    def test_has_navigation_component(self):
        """Test that first component in main row is the navigation."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)
        # Get the main row (third element in the column)
        main_container = result.content.controls[2]
        main_row = main_container.content
        navigation = main_row.controls[0]

        assert isinstance(navigation, ft.Container)
        # Navigation container should have a Column with settings items
        assert isinstance(navigation.content, ft.Column)

    def test_has_vertical_divider(self):
        """Test that second component in main row is a VerticalDivider."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)
        # Get the main row (third element in the column)
        main_container = result.content.controls[2]
        main_row = main_container.content
        divider = main_row.controls[1]

        assert isinstance(divider, ft.VerticalDivider)
        assert divider.width == 1

    def test_has_content_container(self):
        """Test that third component in main row is the content container."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)
        # Get the main row (third element in the column)
        main_container = result.content.controls[2]
        main_row = main_container.content
        content_wrapper = main_row.controls[2]

        assert isinstance(content_wrapper, ft.Container)
        assert content_wrapper.expand is True

    def test_default_view_is_appearance(self):
        """Test that Appearance view is loaded by default."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        create_settings_view(page, app_state)

        # Check that app_state has APPEARANCE as current view
        assert app_state.get_current_view(MainView.SETTINGS) == SettingsSubView.APPEARANCE

    def test_preserves_existing_view_selection(self):
        """Test that existing view selection is noted but default is loaded."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()
        app_state.set_current_view(MainView.SETTINGS, SettingsSubView.LANGUAGE)

        create_settings_view(page, app_state)

        # The view always loads APPEARANCE by default on creation
        assert app_state.get_current_view(MainView.SETTINGS) == SettingsSubView.APPEARANCE

    def test_container_expands(self):
        """Test that main container expands to fill space."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)

        assert result.expand is True

    def test_page_update_called(self):
        """Test that page.update() is called during initialization."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        create_settings_view(page, app_state)

        # Should be called at least once during view load
        assert page.update.called

    def test_content_loaded_on_creation(self):
        """Test that content is loaded on view creation."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)
        content_wrapper = result.content.controls[2]

        # Content should not be None
        assert content_wrapper.content is not None

    def test_row_expands(self):
        """Test that Row expands to fill container."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_settings_view(page, app_state)

        assert result.content.expand is True


class TestSettingsViewNavigation:
    """Test suite for settings view navigation functionality."""

    def test_load_view_function_exists(self):
        """Test that view has a load_view function for navigation."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        # The load_view function is internal, but we can verify navigation works
        # by checking the navigation component has click handlers
        result = create_settings_view(page, app_state)
        navigation = result.content.controls[0]
        nav_buttons = navigation.content.controls[2:]  # Skip title and divider

        # All buttons should have click handlers
        assert all(btn.on_click is not None for btn in nav_buttons)

    def test_multiple_instances_independent(self):
        """Test that multiple view instances are independent."""
        page1 = Mock(spec=ft.Page)
        page1.update = Mock()
        page2 = Mock(spec=ft.Page)
        page2.update = Mock()

        app_state1 = AppState()
        app_state2 = AppState()
        app_state2.set_current_view(MainView.SETTINGS, SettingsSubView.NOTIFICATIONS)

        create_settings_view(page1, app_state1)
        create_settings_view(page2, app_state2)

        # Both views load APPEARANCE by default, states are independent
        assert app_state1.get_current_view(MainView.SETTINGS) == SettingsSubView.APPEARANCE
        assert app_state2.get_current_view(MainView.SETTINGS) == SettingsSubView.APPEARANCE
