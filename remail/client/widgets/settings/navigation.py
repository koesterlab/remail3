"""Settings navigation widget for Flet-based UI."""

from typing import Any, Callable

import flet as ft

from remail.client.state import MainAppState as AppState
from remail.enums import MainView, SettingsSubView


def create_settings_navigation(
    app_state: AppState, on_navigate: Callable[[SettingsSubView], Any]
) -> ft.Container:
    """Create a settings navigation widget.

    Args:
        app_state: The application state object
        on_navigate: Callback function when a navigation item is clicked

    Returns:
        A Container with navigation buttons
    """
    # Define navigation items: (label, SettingsSubView)
    nav_items = [
        ("Appearance", SettingsSubView.APPEARANCE),
        ("Email Accounts", SettingsSubView.EMAIL_ACCOUNTS),
        ("Language & Region", SettingsSubView.LANGUAGE),
        ("Notifications", SettingsSubView.NOTIFICATIONS),
    ]

    buttons: list[ft.TextButton] = []

    for label, sub_view in nav_items:
        # Check if this button is currently active
        is_active = (
            app_state.current_view[0] == MainView.SETTINGS
            and app_state.current_view[1] == sub_view
        )

        # Create button with appropriate styling
        button = ft.TextButton(
            content=ft.Text(label),
            on_click=lambda e, view=sub_view: on_navigate(view),
            style=ft.ButtonStyle(
                color=ft.Colors.PRIMARY if is_active else ft.Colors.ON_SURFACE,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if is_active else None,
            ),
        )
        buttons.append(button)

    # Create container with buttons
    return ft.Container(
        content=ft.Column(
            controls=buttons,
            spacing=16,
        ),
        width=200,
        padding=10,
    )
