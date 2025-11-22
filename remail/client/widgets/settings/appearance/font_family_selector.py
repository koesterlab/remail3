import flet as ft

from remail.client.state.app_state import AppState
from remail.enums import FontFamily


def create_font_family_selector(page: ft.Page, app_state: AppState) -> ft.Column:
    """Create font family selector dropdown."""

    selected_font_family = {"value": app_state.font_family}

    def font_family_changed(e):
        selected_font_family["value"] = FontFamily(e.control.value)

    return ft.Column(
        [
            ft.Text("Font family", weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                value=app_state.font_family.value,
                options=[
                    ft.dropdown.Option(FontFamily.ARIAL.value),
                    ft.dropdown.Option(FontFamily.ROBOTO.value),
                    ft.dropdown.Option(FontFamily.GEORGIA.value),
                    ft.dropdown.Option(FontFamily.COURIER_NEW.value),
                    ft.dropdown.Option(FontFamily.TIMES_NEW_ROMAN.value),
                    ft.dropdown.Option(FontFamily.VERDANA.value),
                    ft.dropdown.Option(FontFamily.TAHOMA.value),
                ],
                width=200,
                on_change=font_family_changed,
            ),
        ],
        spacing=10,
    )
