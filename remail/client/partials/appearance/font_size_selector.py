import flet as ft

from remail.client.state.app_state import AppState


def create_font_size_selector(page: ft.Page, app_state: AppState) -> ft.Column:
    """Create font size selector dropdown."""

    def font_size_changed(e):
        app_state.font_size = e.control.value
        # TODO: Apply font size changes to the page/theme
        page.update()

    return ft.Column(
        [
            ft.Text("Font size", weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                value=app_state.font_size,
                options=[
                    ft.dropdown.Option("Small"),
                    ft.dropdown.Option("Medium"),
                    ft.dropdown.Option("Large"),
                ],
                width=200,
                on_change=font_size_changed,
            ),
        ],
        spacing=10,
    )
