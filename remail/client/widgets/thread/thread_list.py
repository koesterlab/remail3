from __future__ import annotations

import logging

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.thread.message_bubble import MessageBubble
from remail.client.widgets.thread.new_message_dialog import create_new_message_dialog
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.thread_controller import ThreadController
from remail.utils.timer import Timer

_logger = logging.getLogger(__name__)


class ThreadList(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        super().__init__(
            expand=True,
            bgcolor=ft.Colors.SURFACE,
        )
        self.state = state
        self.thread: ThreadDTO | None = None
        state.register_observer(
            MainAppStateProperties.ACTIVE_THREAD, lambda _: self._rebuild()
        )  # if thread changes in state, widget changes
        self._rebuild()

    def _rebuild(self) -> None:
        t_total = Timer()
        new_thread: ThreadPreviewDTO = self.state.get(MainAppStateProperties.ACTIVE_THREAD)
        self.conversation: ConversationDTO = self.state.get(
            MainAppStateProperties.ACTIVE_THREAD_CONVERSATION
        )
        if not new_thread:  # dashboard -> just do nothing
            self.thread = None
            return
        if not self.thread and new_thread.thread_id > 0:
            # Show a loading spinner while the thread is being loaded from the database
            self.content = ft.Column(
                [
                    ft.Container(
                        ft.ProgressRing(),
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    )
                ],
                expand=True,
            )

            # Load the thread from the database in the background so the UI doesn't freeze
            async def load_thread():
                self.thread = ThreadController().get_thread(new_thread.thread_id)
                self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)
                if self.thread is None:
                    return
                self._render()
                try:
                    if self.page:
                        self.update()
                except RuntimeError:
                    pass  # nosec - widget may not be on page

            # Start loading in the background using Flet's task system
            try:
                if self.page:
                    self.page.run_task(load_thread)  # type: ignore[attr-defined]
                else:
                    # Fallback: load synchronously if page is not yet available
                    self.thread = ThreadController().get_thread(new_thread.thread_id)
                    self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)
                    if self.thread is not None:
                        self._render()
            except RuntimeError:
                # Widget not yet added to page, load synchronously
                self.thread = ThreadController().get_thread(new_thread.thread_id)
                self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)
                if self.thread is not None:
                    self._render()
            return
        elif new_thread.thread_id < 0:  # new, unsaved thread
            self.thread = ThreadDTO(-1, new_thread.title, [], self.conversation.contacts)
        self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)
        if self.thread is None:
            return  # just for mypy
        self._render()
        _logger.info("ThreadList._rebuild done. (%s)", t_total.elapsed())

    def _render(self) -> None:
        """Render the thread UI once the thread data is available."""
        if self.thread is None:
            return
        self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)

        header = ft.Container(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.TextField(
                                value=self.thread.title,
                                hint_text="Enter a thread name",
                                content_padding=ft.Padding.all(0),
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
            padding=ft.Padding.only(left=10, top=5, bottom=5, right=10),
            height=60,
            bgcolor=ft.Colors.SURFACE,
        )

        t_widgets = Timer()
        messages_column = ft.Container(
            ft.Column(
                controls=[MessageBubble(m, self.active_user) for m in self.thread.messages],
                spacing=8,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )
        _logger.info(
            "Built %d message bubble(s). (%s)", len(self.thread.messages), t_widgets.elapsed()
        )

        self.content = ft.Column(
            [
                header,
                messages_column,
                create_new_message_dialog(self.state),
            ],
            spacing=0,
            expand=True,
        )