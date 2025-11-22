import flet as ft

from remail.client.partials.appearance import (
    create_font_family_selector,
    create_font_size_selector,
    create_theme_selector,
)
from remail.client.state.app_state import AppState


def appearance_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the appearance settings view with all appearance customization options."""

    return ft.Container(
        ft.Column(
            [
                ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Customize how the app looks and feels"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
                create_theme_selector(page, app_state),
                create_font_size_selector(page, app_state),
                create_font_family_selector(page, app_state),
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )