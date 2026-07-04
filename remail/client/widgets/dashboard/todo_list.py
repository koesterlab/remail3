# remail/client/widgets/dashboard/todo_list.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.state import MainAppState
from remail.client.widgets.dashboard.todo_item import TodoItem, _preview_tags

TodoDict = dict[str, Any]
_FILTER_TAGS = ["All", "Work", "Urgent", "Newsletter", "Finance"]


class TodoList(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        self.state = state
        self.active_filter = "All"
        self.todos = state.thread_controller.get_most_urgent_threads(5)
        self.count_text = ft.Text(
            self._count_label(len(self.todos)),
            size=13,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        self.filter_control = ft.Container(content=self._filter_menu())
        self.items_column = ft.Column(spacing=6)

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "To Do",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        self.count_text,
                    ],
                ),
                self.filter_control,
            ],
        )

        self._refresh_items()

        content_column = ft.Column(
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header_row,
                self.items_column,
            ],
        )

        super().__init__(
            bgcolor=None,
            # bgcolor=ft.Colors.SURFACE,
            padding=ft.Padding.all(15),
            border_radius=24,
            expand=True,
            content=content_column,
        )

    @staticmethod
    def _count_label(count: int) -> str:
        if count == 1:
            return "1 email to answer"
        return f"{count} emails to answer"

    def _filter_menu(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            content=ft.Container(
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                bgcolor=ft.Colors.SURFACE,
                content=ft.Row(
                    tight=True,
                    spacing=6,
                    controls=[
                        ft.Icon(
                            ft.Icons.FILTER_LIST,
                            size=16,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            self.active_filter,
                            size=12,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                ),
            ),
            tooltip="Filter To Do emails",
            items=[self._filter_menu_item(tag) for tag in _FILTER_TAGS],
            style=ft.ButtonStyle(
                padding=ft.Padding.all(0),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

    def _filter_menu_item(self, tag: str) -> ft.PopupMenuItem:
        return ft.PopupMenuItem(
            content=ft.Text(tag, size=13),
            checked=tag == self.active_filter,
            on_click=lambda _e, selected_tag=tag: self._set_filter(selected_tag),
        )

    def _set_filter(self, tag: str) -> None:
        self.active_filter = tag
        self.filter_control.content = self._filter_menu()
        self._refresh_items()
        try:
            self.update()
        except RuntimeError:
            pass

    def _filtered_todos(self):
        if self.active_filter == "All":
            return [todo for todo in self.todos if todo[0].messages]

        return [
            (thread, conversation, user)
            for thread, conversation, user in self.todos
            if thread.messages
            and self.active_filter
            in _preview_tags(thread.title, thread.messages[0].content.body, thread.messages[0].sent_at)
        ]

    def _refresh_items(self) -> None:
        filtered_todos = self._filtered_todos()
        self.count_text.value = self._count_label(len(filtered_todos))
        self.items_column.controls = [
            TodoItem(self.state, thread, user) for thread, conversation, user in filtered_todos
        ]
        if not self.items_column.controls:
            self.items_column.controls = [
                ft.Text(
                    "No emails match this tag",
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            ]
