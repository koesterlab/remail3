import flet as ft

from remail.client.state.app_state import AppState
from remail.enums import FontSize


def create_font_size_selector(_, app_state: AppState) -> ft.Column:
    """Create font size selector dropdown."""

    selected_font_size = {"value": app_state.font_size}

    def font_size_changed(e):
        selected_font_size["value"] = FontSize(e.control.value)

    return ft.Column(
        [
            ft.Text("Font size", weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                value=app_state.font_size.value,
                options=[
                    ft.dropdown.Option(FontSize.SMALL.value),
                    ft.dropdown.Option(FontSize.MEDIUM.value),
                    ft.dropdown.Option(FontSize.LARGE.value),
                ],
                width=200,
                on_select=font_size_changed,
            ),
        ],
        spacing=10,
    )
