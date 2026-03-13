import flet as ft

from remail.client.state.app_state import AppState
from remail.enums import ThemeMode


def create_theme_selector(_, app_state: AppState) -> ft.Column:
    """Create theme selector with radio buttons."""

    selected_theme = {"value": app_state.theme_mode}

    def theme_changed(e):
        selected_theme["value"] = ThemeMode(e.control.value)

    return ft.Column(
        [
            ft.Text("Theme", weight=ft.FontWeight.BOLD),
            ft.RadioGroup(
                ft.Row(
                    [
                        ft.Radio(value=ThemeMode.LIGHT.value, label="Light"),
                        ft.Radio(value=ThemeMode.DARK.value, label="Dark"),
                        ft.Radio(value=ThemeMode.SYSTEM.value, label="System"),
                    ],
                ),
                value=app_state.theme_mode.value,
                on_change=theme_changed,
            ),
        ],
        spacing=10,
    )
