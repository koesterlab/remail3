import flet as ft

from remail.client.state.app_state import AppState
from remail.enums import Language, Timezone


def create_language_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the language & region settings view."""

    def language_changed(e):
        app_state.language = Language(e.control.value)
        # TODO: Apply language changes
        page.update()

    def timezone_changed(e):
        app_state.timezone = Timezone(e.control.value)
        # TODO: Apply timezone changes
        page.update()

    def apply_settings(e):
        # TODO: Apply and persist settings
        page.update()

    return ft.Container(
        ft.Column(
            [
                ft.Text("Language & Region", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Choose your preferred language for the application"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
                ft.Text("Application Language", weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    value=app_state.language.value,
                    options=[ft.dropdown.Option(lang.value) for lang in Language],
                    expand=True,
                    on_change=language_changed,
                ),
                ft.Text("Timezone", weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    value=app_state.timezone.value,
                    options=[ft.dropdown.Option(tz.value) for tz in Timezone],
                    expand=True,
                    on_change=timezone_changed,
                ),
                ft.Container(
                    ft.OutlinedButton("Apply", on_click=apply_settings),
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
