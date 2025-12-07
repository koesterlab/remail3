from typing import Callable, Tuple

import flet as ft

def create_new_message_dialog(on_minimized:Callable[[], None]) -> Tuple[ft.Container, Callable[[], None]]:
    text_field = ft.TextField(
                    min_lines=5,
                    enable_scribble=True,
                    value="Hallo Welt",
                )

    def focus() -> None:
        text_field.focus()


    container = ft.Container(
        ft.Column([
            ft.Container( #control elements
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_DOWNWARD, on_click=lambda _: on_minimized()),
                ]),
                bgcolor=ft.Colors.SURFACE,
            ),
            ft.Container(text_field, bgcolor=ft.Colors.SURFACE),
        ]),
        height=500,
        bgcolor=ft.Colors.SURFACE
    )

    return container, focus