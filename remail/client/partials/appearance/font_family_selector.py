import flet as ft

from remail.client.state.app_state import AppState


def create_font_family_selector(page: ft.Page, app_state: AppState) -> ft.Column:
    """Create font family selector dropdown."""

    def font_family_changed(e):
        app_state.font_family = e.control.value
        # TODO: Apply font family changes to the page/theme
        page.update()

    return ft.Column(
        [
            ft.Text("Font family", weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                value=app_state.font_family,
                options=[
                    ft.dropdown.Option("Arial"),
                    ft.dropdown.Option("Roboto"),
                    ft.dropdown.Option("Georgia"),
                    ft.dropdown.Option("Courier New"),
                    ft.dropdown.Option("Times New Roman"),
                    ft.dropdown.Option("Verdana"),
                    ft.dropdown.Option("Tahoma"),
                ],
                menu_height=200,
                width=200,
                on_change=font_family_changed,
            ),
        ],
        spacing=10,
    )
