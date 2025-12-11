# ---------------------------------------------------------------------- #
# Self-test entry: Allows you to run this file directly for preview.
#   (pixi) python -m remail.client.widgets.thread_widget
# ---------------------------------------------------------------------- #
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.widgets.thread.message_bubble import MessageBubble
from remail.client.widgets.thread.new_message_dialog import create_new_message_dialog
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import ThreadDTO
from tests import fetch_thread

ThreadDict = dict[str, Any]
MessageDict = dict[str, Any]


class ThreadList(ft.Column):
    def __init__(
        self, thread: ThreadPreviewDTO, conversation: ConversationDTO, active_user: ContactDTO
    ) -> None:
        super().__init__(expand=True, spacing=0)
        # input box
        self.input_field = ft.TextField(
            hint_text="Type a reply...",
            border_radius=20,
            filled=True,
            bgcolor="white",
            dense=True,
            expand=True,
            color=ft.Colors.ON_INVERSE_SURFACE,
            fill_color=ft.Colors.INVERSE_SURFACE,
            suffix_icon=ft.Icons.SEND,
            on_focus=lambda _: self.on_input_selected(),
        )

        self.conversation: ConversationDTO = conversation
        self.thread: ThreadDTO = fetch_thread(thread)
        self.active_user = active_user
        self._rebuild()

    # ------------------------------------------------------------------ #
    # rebuild the UI
    # ------------------------------------------------------------------ #
    def _rebuild(self) -> None:
        # ---------- the information of top contact -------- #

        header = ft.Container(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                self.thread.title,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SURFACE,
                            ),
                            ft.Text(
                                str(len(self.thread.messages)) + " messages",
                                size=15,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            padding=ft.padding.only(left=10, top=5, bottom=5, right=10),
            height=60,
        )

        # ---------- “Discussing email”  ---------- #
        # title = str(thread.get("title", "")) or ""
        #
        # if messages_raw:
        #     last_msg = messages_raw[-1]
        #     last_summary = str(last_msg.get("content", {}).get("body", ""))
        # else:
        #     last_summary = ""
        #
        # discussing_card = ft.Container(
        #     width=500,
        #     bgcolor="white",
        #     padding=15,
        #     border_radius=12,
        #     content=ft.Column(
        #         controls=[
        #             ft.Text("Discussing email:", size=12, color="gray"),
        #             ft.Text(title, weight="bold"),
        #             ft.Text(
        #                 last_summary,
        #                 size=12,
        #                 color="gray",
        #                 max_lines=3,
        #                 overflow=ft.TextOverflow.ELLIPSIS,
        #             ),
        #         ],
        #         spacing=4,
        #     ),
        # )

        messages_column = ft.Container(
            ft.Column(
                controls=[MessageBubble(m, self.active_user) for m in self.thread.messages],
                spacing=8,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=ft.Colors.TERTIARY,
            expand=True,
        )

        # ---------- downside message input box ---------- #
        self.dummy_input = ft.Row(
            controls=[
                self.input_field,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        )

        self.input_row = ft.Container(
            content=self.dummy_input, bgcolor=ft.Colors.TERTIARY, padding=ft.padding.all(10)
        )

        # ---------- conbination of the whole layout ---------- #
        self.controls = [
            header,
            # discussing_card,
            # ft.Container(height=20),
            messages_column,
            self.input_row,
        ]

    def on_input_selected(self):
        new_message_dialog, focus_callback = create_new_message_dialog(self.on_input_minimized)
        self.input_row.content = new_message_dialog
        self.input_row.update()
        focus_callback()
        pass

    def on_input_minimized(self):
        self.input_row.content = self.dummy_input
        self.input_row.update()
