# ---------------------------------------------------------------------- #
# Self-test entry: Allows you to run this file directly for preview.
#   (pixi) python -m remail.client.widgets.thread_widget
# ---------------------------------------------------------------------- #
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.thread.message_bubble import MessageBubble
from remail.client.widgets.thread.new_message_dialog import create_new_message_dialog
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.thread_controller import ThreadController

ThreadDict = dict[str, Any]
MessageDict = dict[str, Any]


class ThreadList(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        super().__init__(expand=True, bgcolor=ft.Colors.TERTIARY)
        self.state = state
        self.thread: ThreadDTO | None = None
        state.register_observer(
            MainAppStateProperties.ACTIVE_THREAD, lambda _: self._rebuild()
        )  # if thread changes in state, widget changes
        self._rebuild()

    # ------------------------------------------------------------------ #
    # rebuild the UI
    # ------------------------------------------------------------------ #
    def _rebuild(self) -> None:
        new_thread: ThreadPreviewDTO = self.state.get(MainAppStateProperties.ACTIVE_THREAD)
        self.conversation: ConversationDTO = self.state.get(
            MainAppStateProperties.ACTIVE_CONVERSATION
        )
        if not new_thread:  # dashboard -> just do nothing
            self.thread = None
            return
        if not self.thread and new_thread.thread_id > 0:
            self.thread = ThreadController().get_thread(new_thread.thread_id)
        elif new_thread.thread_id < 0:  # new, unsaved thread
            self.thread = ThreadDTO(-1, new_thread.title, [], self.conversation.contacts)
        self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)
        if self.thread is None:
            return  # just for mypy
        # ---------- the information of top contact -------- #
        header = ft.Container(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.TextField(
                                value=self.thread.title,
                                hint_text="Enter a thread name",
                                content_padding=ft.padding.all(0),
                                collapsed=True,
                                text_style=ft.TextStyle(
                                    size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE
                                ),
                                focused_border_color=ft.Colors.TRANSPARENT,
                                border_color=ft.Colors.TRANSPARENT,
                            ),
                            ft.Text(
                                str(len(self.thread.messages)) + " messages"
                                if len(self.conversation.contacts) == 1
                                else self.conversation.get_member_string(),
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
            bgcolor=ft.Colors.SURFACE,
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
            expand=True,
        )

        # ---------- downside message input box ---------- #

        # ---------- conbination of the whole layout ---------- #
        self.content = ft.Column(
            [
                header,
                # discussing_card,
                # ft.Container(height=20),
                messages_column,
                create_new_message_dialog(self.state),
            ],
            spacing=0,
            expand=True,
        )
