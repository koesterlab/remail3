"""Settings view with navigation and sub-views."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.views.settings.appearance_view import create_appearance_view
from remail.client.views.settings.email_accounts_view import create_email_accounts_view
from remail.client.views.settings.language_view import create_language_view
from remail.client.views.settings.notifications_view import create_notifications_view
from remail.client.views.view_router import ViewRouter
from remail.client.widgets.settings.navigation import create_settings_navigation
from remail.enums import MainView, SettingsSubView


def create_settings_view(page: ft.Page, router:ViewRouter) -> ft.Container:
    """Create the main settings view with navigation and content area.

    Args:
        page: The Flet page object

    Returns:
        A Container with the settings view
    """
    page.title = "Settings"

    # Back to dashboard button
    def navigate_to_dashboard(e):
        """Navigate back to dashboard."""
        if router:
            page.clean()
            dashboard_view = router.load_view(MainView.DASHBOARD)
            page.add(dashboard_view)
            page.update()

    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Back to Dashboard",
        on_click=navigate_to_dashboard,
    )

    # Content container that will hold the active sub-view
    content_container = ft.Ref[ft.Container]()

    def load_view(view_name: SettingsSubView):
        """Load a settings sub-view into the content area."""
        if view_name == SettingsSubView.APPEARANCE:
            content_container.current.content = create_appearance_view(page)
        elif view_name == SettingsSubView.EMAIL_ACCOUNTS:
            content_container.current.content = create_email_accounts_view(page)
        elif view_name == SettingsSubView.LANGUAGE:
            content_container.current.content = create_language_view(page)
        elif view_name == SettingsSubView.NOTIFICATIONS:
            content_container.current.content = create_notifications_view(page)

        page.update()

    initial_sub_view = app_state.settings_start_sub_view or SettingsSubView.APPEARANCE
    app_state.settings_start_sub_view = None

    # Set default view
    app_state.set_current_view(MainView.SETTINGS, initial_sub_view)

    # Create navigation
    navigation = create_settings_navigation(app_state, load_view)

    # Create header with back button
    header = ft.Container(
        content=ft.Row(
            [
                back_button,
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ],
        ),
        padding=ft.padding.only(left=10, top=10, bottom=10),
    )

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
    load_view(initial_sub_view)

    return ft.Container(
        content=ft.Column(
            [
                header,
                ft.Divider(height=1),
                ft.Container(content=main_row, expand=True),
            ],
            expand=True,
        ),
        expand=True,
    )
