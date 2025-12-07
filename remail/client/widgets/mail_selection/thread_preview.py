from collections.abc import Callable

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.conversations import ThreadPreviewDTO


class ThreadPreview(ft.Container):
    # component representing a single contact entry
    def __init__(
        self, thread: ThreadPreviewDTO, state: MainAppState):
        super().__init__(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        (
                                            "(" + str(thread.unread_count) + ") "
                                            if thread.unread_count > 0
                                            else ""
                                        )
                                        + thread.title,
                                        weight=ft.FontWeight.BOLD
                                        if thread.unread_count > 0
                                        else ft.FontWeight.NORMAL,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        thread.last_message,
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
            on_click=lambda _: state.set(MainAppStateProperties.ACTIVE_THREAD, thread),
            padding=12,
        )
