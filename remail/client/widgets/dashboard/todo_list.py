# remail/client/widgets/dashboard/todo_list.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.state import MainAppState
from remail.client.widgets.dashboard.todo_item import TodoItem

TodoDict = dict[str, Any]


class TodoList(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        # Show a loading indicator while the todos are being loaded from the database
        super().__init__(
            bgcolor=None,
            padding=ft.Padding.all(15),
            border_radius=24,
            expand=True,
            content=ft.Column(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(
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
                                        "Loading...",
                                        size=13,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.ProgressRing(),  # Show spinner while loading
                ],
            ),
        )

        # Load the todos from the database in the background so the UI doesn't freeze
        # Without async, this can take several seconds and block the dashboard from opening
        async def load_todos():
            todos = state.thread_controller.get_most_urgent_threads(5)

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
                                f"{len(todos)} emails to answer",
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
                    for thread, conversation, user in todos
                    if thread.messages
                ],
            )

            # Update the UI with the loaded todos
            self.content = ft.Column(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[header_row, items_column],
            )
            if self.page:
                self.update()

        # Store the coroutine to be started when the page is available
        self._load_todos = load_todos

    def did_mount(self):
        # Start loading todos when the widget is added to the page
        self.page.run_task(self._load_todos)