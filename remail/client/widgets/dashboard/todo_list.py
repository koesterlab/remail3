# remail/client/widgets/dashboard/todo_list.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.state import MainAppState
from remail.client.widgets.dashboard.todo_item import TodoItem

TodoDict = dict[str, Any]


class TodoList(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        self.todos = state.thread_controller.get_most_urgent_threads(5)
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
                        ft.Text(
                            f"{len(self.todos)} emails to answer",
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                ),
            ],
        )

        items_column = ft.Column(
            spacing=6,
            controls=[
                TodoItem(state, thread, user)
                for thread, conversation, user in self.todos
                if thread.messages
            ],
        )

        content_column = ft.Column(
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header_row,
                items_column,
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
