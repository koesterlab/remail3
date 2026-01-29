from datetime import UTC

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO


class ThreadPreview(ft.Container):
    # component representing a single contact entry
    def __init__(
        self, state: MainAppState, thread: ThreadPreviewDTO, conversation: ConversationDTO
    ):
        def on_click():
            state.set(MainAppStateProperties.ACTIVE_CONVERSATION, conversation)
            state.set(MainAppStateProperties.ACTIVE_THREAD, thread)

        super().__init__(
            content=ft.Column(
                [
                    ft.Text(
                        ("(" + str(thread.unread_count) + ") " if thread.unread_count > 0 else "")
                        + thread.title,
                        max_lines=1,
                        weight=ft.FontWeight.BOLD
                        if thread.unread_count > 0
                        else ft.FontWeight.NORMAL,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                thread.last_message,
                                size=12,
                                max_lines=1,
                                expand=True,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                thread.last_message_datetime.replace(tzinfo=UTC).strftime(
                                    "%d.%m.%Y"
                                ),  # todo: variable time zone
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ]
            ),
            on_click=lambda _: on_click(),
            padding=ft.padding.all(12),
        )
