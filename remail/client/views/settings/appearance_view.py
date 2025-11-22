"""Appearance settings view."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.settings.appearance import (
    create_font_family_selector,
    create_font_size_selector,
    create_theme_selector,
)
from remail.enums import ThemeMode


def create_appearance_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the appearance settings view with all appearance customization options.

    Args:
        page: The Flet page object
        app_state: The application state

    Returns:
        A Container with the appearance settings view
    """

    theme_selector = create_theme_selector(page, app_state)
    font_size_selector = create_font_size_selector(page, app_state)
    font_family_selector = create_font_family_selector(page, app_state)

    def apply_appearance_settings(e):
        """Apply the selected appearance settings."""

        theme = theme_selector.controls[1].value  # RadioGroup value
        app_state.theme_mode = ThemeMode(theme)

        if app_state.theme_mode == ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.LIGHT
        elif app_state.theme_mode == ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM

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
