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

        if new_thread.thread_id < 0:  # new, unsaved thread
            self.thread = ThreadDTO(-1, new_thread.title, [], self.conversation.contacts)
            self._render()
        elif not self.thread or self.thread.id != new_thread.thread_id:
            # Load the thread directly since page may not be available yet
            self.thread = ThreadController().get_thread(new_thread.thread_id)
            self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)
            if self.thread is not None:
                self._render()
        else:
            self._render()

        _logger.info("ThreadList._rebuild done. (%s)", t_total.elapsed())

    def _render(self) -> None:
        """Render the thread UI once the thread data is available."""
        if self.thread is None:
            return
        self.active_user = self.state.get(MainAppStateProperties.ACTIVE_USER)

        # ---------- the information of top contact -------- #

        # This function is called when the user clicks the delete button
        def on_delete_click(_):
            # This function is called when the user confirms the deletion
            def confirm_delete(_):
                thread_id = self.thread.id if self.thread else None
                if not thread_id:
                    return
                print(f"Deleting thread with id: {thread_id}")
                # Delete the thread from the database
                ThreadController().delete_thread(thread_id)

                # Remove deleted thread from the left side list
                # We modify threads in place and set a new list reference to force UI update
                displayed = self.state.get(MainAppStateProperties.DISPLAYED_MAILS)
                thread_id = self.thread.id
                from dataclasses import replace

                new_displayed = [
                    replace(conv, threads=[t for t in conv.threads if t.thread_id != thread_id])
                    for conv in displayed
                ]
                self.state._values[MainAppStateProperties.DISPLAYED_MAILS] = []
                self.state.set(MainAppStateProperties.DISPLAYED_MAILS, new_displayed)

                # Force complete reload of the conversation list
                self.state.set(MainAppStateProperties.ACTIVE_CONVERSATION, None)
                self.state.set(MainAppStateProperties.ACTIVE_THREAD, None)
                dialog.open = False
                self.page.update()

            # This function is called when the user cancels the deletion
            def cancel_delete(_):
                # Just close the dialog, do nothing
                dialog.open = False
                self.page.update()

            # Show a confirmation popup before deleting
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Delete Thread"),
                content=ft.Text(f'Are you sure you want to delete "{self.thread.title}"?'),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(
                            color=ft.Colors.ERROR
                        ),  # Red color for destructive action
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

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
                        expand=True,  # Expand the column to fill available space
                    ),
                    ft.IconButton(  # Delete button in the top right corner of the thread header
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.ERROR,  # Red color to indicate a destructive action
                        tooltip="Delete thread",  # Shown on hover
                        on_click=on_delete_click,  # Calls the function we defined above
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Push column to left, button to right
                vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Vertically center both items
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
