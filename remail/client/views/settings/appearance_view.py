"""Appearance settings view."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.settings.appearance import (
    create_font_family_selector,
    create_font_size_selector,
    create_theme_selector,
)
from remail.controllers import SettingsController
from remail.controllers.dtos import SettingsDTO


def create_appearance_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the appearance settings view with all appearance customization options.

    Args:
        page: The Flet page object
        app_state: The application state

    Returns:
        A Container with the appearance settings view
    """

    controller = SettingsController()
    settings_data: SettingsDTO = controller.get_settings()

    theme_selector = create_theme_selector(page, app_state)
    font_size_selector = create_font_size_selector(page, app_state)
    font_family_selector = create_font_family_selector(page, app_state)

    # Load saved settings into UI controls
    # Set theme
    if hasattr(theme_selector.controls[1], "value"):
        theme_selector.controls[1].value = settings_data.theme_mode

    # Set font size if available
    if len(font_size_selector.controls) > 1 and hasattr(
        font_size_selector.controls[1], "value"
    ):
        font_size_selector.controls[1].value = settings_data.font_size

    # Set font family if available
    if len(font_family_selector.controls) > 1 and hasattr(
        font_family_selector.controls[1], "value"
    ):
        font_family_selector.controls[1].value = settings_data.font_family

    def apply_appearance_settings(e):
        """Apply the selected appearance settings."""

        theme = ft.ThemeMode(theme_selector.controls[1].value)  # RadioGroup value
        settings_data.font_size = (
            font_size_selector.controls[1].value
            if len(font_size_selector.controls) > 1
            else "medium"
        )
        settings_data.font_family = (
            font_family_selector.controls[1].value
            if len(font_family_selector.controls) > 1
            else "system"
        )

        # Update app state
        app_state.theme_mode = theme
        page.theme_mode = theme

        # Save to database using controller
        controller.update_settings(settings_data)

        # Show success message
        snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully"),
            bgcolor=ft.Colors.GREEN,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True

        # TODO: Apply font size changes to the page/theme
        # TODO: Apply font family changes to the page/theme

        page.update()

    return ft.Container(
        ft.Column(
            [
                ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Customize how the app looks and feels"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
                theme_selector,
                font_size_selector,
                font_family_selector,
                ft.Container(
                    ft.OutlinedButton("Apply", on_click=apply_appearance_settings),
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
