from collections.abc import Callable

import flet as ft

from remail.client.state.app_state import AppState
from remail.enums import MainView, SettingsSubView


def create_settings_navigation(app_state: AppState, on_navigate: Callable) -> ft.Container:
    """Create the settings navigation menu.

    Args:
        app_state: The application state
        on_navigate: Callback function to handle navigation (receives view_name as parameter)

    Returns:
        A Column with the navigation menu
    """

    nav_items = ft.Ref[ft.Column]()

    def create_nav_item(label: str, view_name: SettingsSubView) -> ft.TextButton:
        """Create a navigation item for the settings menu."""

        def on_click(e):
            app_state.set_current_view(MainView.SETTINGS, view_name)
            on_navigate(view_name)
            update_nav_items()

        is_active = app_state.get_current_view(MainView.SETTINGS) == view_name

        return ft.TextButton(
            text=label,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=ft.Colors.PRIMARY if is_active else ft.Colors.ON_SURFACE,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if is_active else None,
            ),
        )

    def update_nav_items():
        """Rebuild navigation items with updated active state."""

        nav_items.current.controls = [
            create_nav_item("Appearance", SettingsSubView.APPEARANCE),
            create_nav_item("Email Accounts", SettingsSubView.EMAIL_ACCOUNTS),
            create_nav_item("Language & Region", SettingsSubView.LANGUAGE),
            create_nav_item("Notifications", SettingsSubView.NOTIFICATIONS),
        ]

        nav_items.current.update()

    return ft.Container(
        ft.Column(
            ref=nav_items,
            controls=[
                create_nav_item("Appearance", SettingsSubView.APPEARANCE),
                create_nav_item("Email Accounts", SettingsSubView.EMAIL_ACCOUNTS),
                create_nav_item("Language & Region", SettingsSubView.LANGUAGE),
                create_nav_item("Notifications", SettingsSubView.NOTIFICATIONS),
            ],
            spacing=16,
        ),
        width=200,
        padding=10,
    )
