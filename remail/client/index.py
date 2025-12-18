"""Main entry point for the Remail client application."""

import flet as ft

from remail.client.state import AppState
from remail.client.state.settings_loader import load_settings_into_state
from remail.client.views.main.main_view import create_main_view
from remail.client.views.settings.settings_view import create_settings_view
from remail.client.views.view_router import ViewRouter
from remail.enums import MainView


def main(page: ft.Page):
    """Initialize and run the Remail application.

    Args:
        page: The Flet page object
    """

    page.title = "Remail 2.0"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    app_state = AppState()
    load_settings_into_state(app_state, page)

    # Create router and register views
    router = ViewRouter(page, app_state)
    app_state.router = router
    router.register_view(MainView.SETTINGS, create_settings_view)
    router.register_view(MainView.DASHBOARD, create_main_view)

    # Load initial view (Settings)
    router.load_view(MainView.DASHBOARD)

if __name__ == "__main__":
    ft.app(main)
