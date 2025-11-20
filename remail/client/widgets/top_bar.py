from __future__ import annotations

from collections.abc import Callable

import flet as ft


class TopBar(ft.Row):
    """Top bar with only Settings button on the right."""

    def __init__(self, on_settings: Callable[[], None] | None = None) -> None:
        super().__init__()
        self.alignment = ft.MainAxisAlignment.END
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.height = 50
        self.expand = False

        settings_button = ft.ElevatedButton(
            text="Settings",
            on_click=lambda e: on_settings() if on_settings is not None else None,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
        )

        self.controls = [settings_button]
