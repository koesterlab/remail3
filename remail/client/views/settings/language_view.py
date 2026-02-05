import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers import SettingsController
from remail.enums import Language, Timezone


def create_language_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the language & region settings view."""

    controller = SettingsController()
    current_settings = controller.get_settings()

    # Load current language and timezone settings if available
    if current_settings:
        try:
            app_state.language = Language(current_settings.language)
        except (ValueError, KeyError):
            pass
        try:
            app_state.timezone = Timezone(current_settings.timezone)
        except (ValueError, KeyError):
            pass

    def language_changed(e):
        app_state.language = Language(e.control.value)
        page.update()

    def timezone_changed(e):
        app_state.timezone = Timezone(e.control.value)
        page.update()

    def apply_settings(e):
        # Save language and timezone settings to database
        controller.update_settings(
            language=app_state.language.value,
            timezone=app_state.timezone.value,
        )

        # Show success message
        snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully"),
            bgcolor=ft.Colors.GREEN,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True

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
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
        expand=True,
    )
