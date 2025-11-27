"""Settings view with navigation and sub-views."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.views.settings.appearance_view import create_appearance_view
from remail.client.views.settings.email_accounts_view import create_email_accounts_view
from remail.client.views.settings.language_view import create_language_view
from remail.client.views.settings.notifications_view import create_notifications_view
from remail.client.widgets.settings.navigation import create_settings_navigation
from remail.enums import MainView, SettingsSubView


def create_settings_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the main settings view with navigation and content area.

    Args:
        page: The Flet page object
        app_state: The application state

    Returns:
        A Container with the settings view
    """
    page.title = "Settings"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # Content container that will hold the active sub-view
    content_container = ft.Ref[ft.Container]()

    def load_view(view_name: SettingsSubView):
        """Load a settings sub-view into the content area."""
        if view_name == SettingsSubView.APPEARANCE:
            content_container.current.content = create_appearance_view(page, app_state)
        elif view_name == SettingsSubView.EMAIL_ACCOUNTS:
            content_container.current.content = create_email_accounts_view(page, app_state)
        elif view_name == SettingsSubView.LANGUAGE:
            content_container.current.content = create_language_view(page, app_state)
        elif view_name == SettingsSubView.NOTIFICATIONS:
            content_container.current.content = create_notifications_view(page, app_state)

        page.update()

    # Set default view to APPEARANCE
    app_state.set_current_view(MainView.SETTINGS, SettingsSubView.APPEARANCE)

    # Create navigation
    navigation = create_settings_navigation(app_state, load_view)

    # Create main layout
    main_row = ft.Row(
        controls=[
            navigation,
            ft.VerticalDivider(width=1),
            ft.Container(
                ref=content_container,
                expand=True,
            ),
        ],
        expand=True,
    )

    # Load initial view
    load_view(SettingsSubView.APPEARANCE)

    return ft.Container(
        content=main_row,
        expand=True,
    )
