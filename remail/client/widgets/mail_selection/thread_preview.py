from collections.abc import Callable

import flet as ft

from remail.controllers.dtos.conversations import ThreadPreviewDTO


class ThreadPreview(ft.Container):
    # component representing a single contact entry
    def __init__(
        self, topic: ThreadPreviewDTO, on_click: Callable[[ThreadPreviewDTO | None], None]
    ):
        super().__init__(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        (
                                            "(" + str(topic.unread_count) + ") "
                                            if topic.unread_count > 0
                                            else ""
                                        )
                                        + topic.title,
                                        weight=ft.FontWeight.BOLD
                                        if topic.unread_count > 0
                                        else ft.FontWeight.NORMAL,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        topic.last_message,
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=6,
                            ),
                        ],
                        spacing=3,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            on_click=lambda _: on_click(topic),
            padding=12,
        )
