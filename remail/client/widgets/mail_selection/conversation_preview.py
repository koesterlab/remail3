from collections.abc import Callable

import flet as ft


class ConversationPreview(ft.Container):
    # component representing a single contact entry
    def __init__(
        self,
        image: ft.Control,
        primary_text: str,
        secondary_text: str,
        fav: bool,
        registered: bool,
        on_toggle_fav: Callable[[], None],
        on_click: Callable[[], None],
    ):
        image.color = ft.Colors.ON_SECONDARY
        icon_btn = ft.Row([], spacing=2, expand=True, alignment=ft.MainAxisAlignment.END)

        if not registered:
            icon_btn.controls = [
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_color=ft.Colors.ON_SURFACE,
                    tooltip="Zu Kontakten hinzufügen",
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE, icon_color=ft.Colors.ON_SURFACE_VARIANT, tooltip="Spam"
                ),
            ]

            def on_hover(e):
                pass
        else:
            fav_button = ft.IconButton(
                icon=ft.Icons.STAR if fav else ft.Icons.STAR_OUTLINE,
                tooltip="Favorit",
                on_click=lambda e: on_toggle_fav(),
                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                visible=fav,
            )
            icon_btn.controls = [fav_button]

            def on_hover(e):
                fav_button.visible = fav or e.data == "true"
                fav_button.update()

        super().__init__(
            on_hover=on_hover,
            on_click=lambda e: on_click(),
            bgcolor=ft.Colors.TRANSPARENT,
            margin=0,
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY)),
            content=ft.Row(
                [
                    ft.CircleAvatar(content=image, bgcolor=ft.Colors.ON_SURFACE, radius=20),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        primary_text,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        secondary_text, size=12, color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=6,
                            ),
                        ],
                        spacing=3,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    icon_btn,
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=12,
        )
