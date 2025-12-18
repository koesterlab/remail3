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
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import ThreadDTO
from tests import fetch_thread

ThreadDict = dict[str, Any]
MessageDict = dict[str, Any]


class ThreadList(ft.Column):
    def __init__(
        self, state:MainAppState
    ) -> None:
        super().__init__(expand=True, spacing=0)
        self.state = state
        self.thread: ThreadDTO|None = None
        state.register_observer(MainAppStateProperties.ACTIVE_THREAD, lambda _: self._rebuild()) #if thread changes in state, widget changes
        self._rebuild()

    # ------------------------------------------------------------------ #
    # rebuild the UI
    # ------------------------------------------------------------------ #
    def _rebuild(self) -> None:
        new_thread: ThreadPreviewDTO = self.state.get(MainAppStateProperties.ACTIVE_THREAD)
        if not new_thread: #dashboard -> just do nothing
            self.thread = None
            return
        if not self.thread: #or new_thread.thread_id != self.thread.id: #new thread #todo: threads ids geben
            self.thread = fetch_thread(new_thread)

        self.conversation = next( #could be better
                filter(
                    lambda conv: new_thread in conv.threads,
                    self.state.get(MainAppStateProperties.DISPLAYED_MAILS),
                )
            )
        self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)

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

        # ---------- conbination of the whole layout ---------- #
        self.controls = [
            header,
            # discussing_card,
            # ft.Container(height=20),
            messages_column,
            create_new_message_dialog(self.state),
        ]
