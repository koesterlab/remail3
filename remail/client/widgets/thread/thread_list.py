from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.thread.message_bubble import MessageBubble
from remail.client.widgets.thread.new_message_dialog import create_new_message_dialog
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.tag_controller import TagController
from remail.controllers.thread_controller import ThreadController
from remail.models import Tag

ThreadDict = dict[str, Any]
MessageDict = dict[str, Any]

_TAG_COLORS: dict[str, str] = {
    "Work": ft.Colors.BLUE,
    "Personal": ft.Colors.GREEN,
    "Urgent": ft.Colors.RED,
    "Newsletter": ft.Colors.ORANGE,
    "Finance": ft.Colors.PURPLE,
}
_FALLBACK_COLORS = (ft.Colors.TEAL, ft.Colors.CYAN, ft.Colors.INDIGO, ft.Colors.BROWN)


def _tag_color(name: str, index: int = 0) -> str:
    return _TAG_COLORS.get(name, _FALLBACK_COLORS[index % len(_FALLBACK_COLORS)])


class TagBar(ft.Container):
    """Tag chips and add/remove actions for the currently opened thread."""

    def __init__(self, thread_id: int) -> None:
        self.thread_id = thread_id
        self.tag_controller = TagController()
        self.applied_tags: list[Tag] = []
        super().__init__(
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            bgcolor=ft.Colors.SURFACE,
        )
        self.refresh()

    def _update_if_mounted(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass

    def refresh(self) -> None:
        self.applied_tags = self.tag_controller.get_tags_for_thread(self.thread_id)
        controls: list[ft.Control] = [
            self._tag_chip(tag, index) for index, tag in enumerate(self.applied_tags)
        ]
        controls.append(
            ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                tooltip="Add tag",
                icon_size=18,
                on_click=self._open_add_dialog,
            )
        )
        self.content = ft.Row(controls=controls, spacing=6, wrap=True)
        self._update_if_mounted()

    def _tag_chip(self, tag: Tag, index: int) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(tag.name, size=11, color=ft.Colors.WHITE),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=12,
                        icon_color=ft.Colors.WHITE,
                        tooltip=f"Remove {tag.name}",
                        on_click=lambda _, current_tag=tag: self._remove_tag(current_tag),
                        padding=ft.Padding.all(0),
                        height=18,
                        width=18,
                    ),
                ],
                spacing=2,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=_tag_color(tag.name, index),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
        )

    def _remove_tag(self, tag: Tag) -> None:
        if tag.id is None:
            return
        self.tag_controller.remove_tag_from_thread(self.thread_id, tag.id)
        self.refresh()

    def _open_add_dialog(self, _: ft.ControlEvent) -> None:
        applied_ids = {tag.id for tag in self.applied_tags}
        available_tags = [
            tag for tag in self.tag_controller.get_all_tags() if tag.id not in applied_ids
        ]

        def close_dialog(dialog: ft.AlertDialog) -> None:
            dialog.open = False
            try:
                self.page.update()
            except RuntimeError:
                pass

        def add_tag(tag: Tag, dialog: ft.AlertDialog) -> None:
            if tag.id is None:
                return
            self.tag_controller.add_tag_to_thread(self.thread_id, tag.id)
            close_dialog(dialog)
            self.refresh()

        dialog = ft.AlertDialog(
            title=ft.Text("Add tag"),
            content=(
                ft.Column(
                    controls=[
                        ft.TextButton(
                            tag.name,
                            on_click=lambda _, current_tag=tag: add_tag(current_tag, dialog),
                        )
                        for tag in available_tags
                    ],
                    tight=True,
                    spacing=4,
                )
                if available_tags
                else ft.Text("All available tags are already assigned.")
            ),
            actions=[ft.TextButton("Cancel", on_click=lambda _: close_dialog(dialog))],
        )
        try:
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except RuntimeError:
            pass


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
            MainAppStateProperties.ACTIVE_THREAD_CONVERSATION
        )
        if not new_thread:  # dashboard -> just do nothing
            self.thread = None
            return
        if new_thread.thread_id > 0 and (
            self.thread is None or self.thread.id != new_thread.thread_id
        ):
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

        self.content = ft.Column(
            [
                header,
                TagBar(new_thread.thread_id) if new_thread.thread_id > 0 else ft.Container(),
                ft.Divider(height=1),
                # discussing_card,
                # ft.Container(height=20),
                messages_column,
                create_new_message_dialog(self.state),
            ],
            spacing=0,
            expand=True,
        )
