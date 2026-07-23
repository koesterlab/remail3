# remail/client/widgets/dashboard/todo_list.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.dashboard.todo_item import TodoItem

TodoDict = dict[str, Any]


class TodoList(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        self.state = state

        # Initially show all To Do threads.
        self.todos = state.thread_controller.get_most_urgent_threads(5)

        self.count_text = ft.Text(
            f"{len(self.todos)} emails to answer",
            size=13,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )

        self.items_column = ft.Column(
            spacing=6,
            controls=self._build_todo_items(),
        )

        self.tag_filter = ft.Dropdown(
            value="all",
            width=160,
            options=self._build_tag_options(),
            on_select=self._on_tag_selected,
        )
        state.register_observer(
            MainAppStateProperties.TAGS_CHANGED,
            self._on_tags_changed,
            weak=True,
        )

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
                self.tag_filter,
            ],
        )

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
            padding=ft.Padding.all(15),
            border_radius=24,
            expand=True,
            content=content_column,
        )

    def _build_todo_items(self) -> list[ft.Control]:
        """Build the visible cards from the current thread results."""
        items: list[ft.Control] = [
            TodoItem(self.state, thread, user)
            for thread, conversation, user in self.todos
            if thread.messages
        ]
        if items:
            return items

        return [
            ft.Text(
                "No To Do emails match this tag.",
                color=ft.Colors.ON_SURFACE_VARIANT,
                italic=True,
            )
        ]

    def _build_tag_options(self) -> list[ft.DropdownOption]:
        tags = self.state.tag_controller.get_all_tags()
        return [
            ft.DropdownOption(key="all", text="All tags"),
            *[
                ft.DropdownOption(key=str(tag.id), text=tag.name)
                for tag in tags
                if tag.id is not None
            ],
        ]

    def _on_tags_changed(self, _: object) -> None:
        self.tag_filter.options = self._build_tag_options()
        valid_values = {option.key for option in self.tag_filter.options}

        if self.tag_filter.value not in valid_values:
            self.tag_filter.value = "all"

        self._reload_todos()
        self.update()

    def _on_tag_selected(self, event) -> None:
        """Reload the To Do threads using the selected tag."""
        self.tag_filter.value = event.control.value
        self._reload_todos()
        self.update()

    def _reload_todos(self) -> None:
        """Reload cards and count for the currently selected persisted tag."""
        selected_value = self.tag_filter.value

        if selected_value == "all":
            tag_id = None
        else:
            if selected_value is None:
                raise ValueError("The To Do tag filter has no selected value")
            tag_id = int(selected_value)

        self.todos = self.state.thread_controller.get_most_urgent_threads(
            count=5,
            tag_id=tag_id,
        )

        self.count_text.value = f"{len(self.todos)} emails to answer"
        self.items_column.controls = self._build_todo_items()
