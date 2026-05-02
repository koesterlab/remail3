from collections.abc import Callable
from typing import Any

import flet as ft

from remail.controllers.dtos import SettingsDTO
from remail.controllers.settings_controller import SettingsController


class SettingsSubView(ft.Container):
    def __init__(self):
        self.controller = SettingsController()
        self.settings: SettingsDTO = self.controller.get_settings()
        self._settings_change_handler: list[Callable[[], None]] = []
        super().__init__(content=self.create_page(self.settings))

    def create_page(self, settings: SettingsDTO) -> ft.Container:
        return ft.Container()

    def apply_settings(self, key: str, value: Any):
        # Save all notification settings to database
        setattr(self.settings, key, value)
        self.controller.update_settings(self.settings)
        self.settings = self.controller.get_settings()

        # Show success message
        snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully"),
            bgcolor=ft.Colors.GREEN,
        )
        snack_bar.open = True
        self.content = self.create_page(self.settings)
        self.update()
