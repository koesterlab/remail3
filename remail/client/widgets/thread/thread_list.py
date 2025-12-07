# ---------------------------------------------------------------------- #
# Self-test entry: Allows you to run this file directly for preview.
#   (pixi) python -m remail.client.widgets.thread_widget
# ---------------------------------------------------------------------- #
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.widgets.thread.message_bubble import MessageBubble
from tests import fetch_thread
from remail.controllers.dtos.conversations import ThreadPreviewDTO, ConversationDTO, ContactDTO
from remail.controllers.dtos.threads import ThreadDTO

ThreadDict = dict[str, Any]
MessageDict = dict[str, Any]


class ThreadList(ft.Column):
    def __init__(self, thread:ThreadPreviewDTO, conversation: ConversationDTO, active_user:ContactDTO) -> None:
        super().__init__()
        self.spacing = 10
        self.expand = True
        # input box
        self.input_field = ft.TextField(
            hint_text="Type a reply...",
            border_radius=20,
            filled=True,
            bgcolor="white",
            dense=True,
            expand=True,
        )

        self.conversation: ConversationDTO = conversation
        self.thread:ThreadDTO = fetch_thread(thread)
        self.active_user = active_user
        self._rebuild()

    # ------------------------------------------------------------------ #
    # load external API
    # ------------------------------------------------------------------ #
    def set_thread(self, thread: ThreadDict) -> None:
        # update current UI
        self.thread = thread
        self._rebuild()
        self.update()


    # ------------------------------------------------------------------ #
    # rebuild the UI
    # ------------------------------------------------------------------ #
    def _rebuild(self) -> None:

        # ---------- the information of top contact -------- #

        header = ft.Container(ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(self.thread.title, size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                        ft.Text(str(len(self.thread.messages)) + " messages", size=15, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,

        ),
            padding=ft.padding.only(left=10, top=5, bottom=5, right=10),
            height=50
        )

        # ---------- “Discussing email” 卡片 ---------- #
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

        messages_column = ft.Container(ft.Column(
            controls=[MessageBubble(m, self.active_user) for m in self.thread.messages],
            spacing=8,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ), bgcolor=ft.Colors.TERTIARY)

        # ---------- downside message input box ---------- #
        input_row = ft.Row(
            controls=[
                self.input_field,
                ft.IconButton(
                    icon=ft.Icons.SEND,
                    disabled=True,  # stake holder
                    tooltip="Send (coming soon)",
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        )

        # ---------- conbination of the whole layout ---------- #
        self.controls = [
            header,
            #discussing_card,
            #ft.Container(height=20),
            messages_column,
            input_row,
        ]