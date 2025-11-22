import flet as ft

from remail.client.state.app_state import AppState


def create_theme_selector(page: ft.Page, app_state: AppState) -> ft.Column:
    """Create theme selector with radio buttons and apply action."""

    selected_theme = {"value": app_state.theme_mode}

    def theme_changed(e):
        selected_theme["value"] = e.control.value

    def apply_theme(e):
        theme = selected_theme["value"]
        app_state.theme_mode = theme

        if theme == "light":
            page.theme_mode = ft.ThemeMode.LIGHT

        elif theme == "dark":
            page.theme_mode = ft.ThemeMode.DARK

        else:
            page.theme_mode = ft.ThemeMode.SYSTEM

        page.update()

    return ft.Column(
        [
            ft.Text("Theme", weight=ft.FontWeight.BOLD),
            ft.RadioGroup(
                ft.Row(
                    [
                        ft.Radio(value="light", label="Light"),
                        ft.Radio(value="dark", label="Dark"),
                        ft.Radio(value="system", label="System"),
                    ],
                ),
                value=app_state.theme_mode,
                on_change=theme_changed,
            ),
            ft.Container(
                ft.OutlinedButton("Apply", on_click=apply_theme),
                alignment=ft.alignment.center,
            ),
        ],
        spacing=10,
    )
