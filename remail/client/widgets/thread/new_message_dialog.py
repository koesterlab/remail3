from collections.abc import Callable

import flet as ft
from flet.core.control_event import ControlEvent

from remail.client.state import MainAppState, MainAppStateProperties


def create_new_message_dialog(state: MainAppState) -> ft.Container:
    expanded = False
    def expand() -> None:
        nonlocal expanded
        expanded = True
        input_field.max_lines = 10
        input_field.min_lines = 10
        input_field.dense = False
        input_field.update()

        pass

    def collapse() -> None:
        nonlocal expanded
        expanded = False
        input_field.max_lines = 1
        input_field.min_lines = 1
        input_field.dense = True
        input_field.update()

        pass


    input_field = ft.TextField(
            hint_text="Type a reply...",
            border_radius=20,
            min_lines=1,
            max_lines=1,
            filled=True,
            bgcolor=ft.Colors.TRANSPARENT,
            expand=True,
            color=ft.Colors.TRANSPARENT,
            fill_color=ft.Colors.TRANSPARENT,
            on_focus=lambda _: expand(),
            on_blur=lambda e: state.set(MainAppStateProperties.DRAFT, input_field.value),
    )

    def on_draft_change(s):
        input_field.value = s
        if not expanded:
            expand()

    state.register_observer(MainAppStateProperties.DRAFT, on_draft_change)

    container = ft.Container(ft.Stack([
        input_field, ft.IconButton(ft.Icons.ARROW_DOWNWARD, on_click=lambda _: collapse()),
    ]), bgcolor=ft.Colors.TRANSPARENT)

    return container
