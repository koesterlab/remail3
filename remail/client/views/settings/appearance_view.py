"""Appearance settings view."""

import flet as ft
from flet import ThemeMode

from remail.client.views.settings.settings_sub_view import SettingsSubView
from remail.controllers.dtos import SettingsDTO
from remail.enums import FontFamily, FontSize


class AppearanceView(SettingsSubView):
    def _apply_theme_mode(self, value: str) -> None:
        theme_mode = ThemeMode(value)
        if self.page is not None:
            self.page.theme_mode = theme_mode or ThemeMode.SYSTEM
        self.apply_settings("theme_mode", theme_mode)

    def _apply_font_size(self, value: str) -> None:
        font_size = FontSize(value)
        self.apply_settings("font_size", font_size)

    def _apply_font_family(self, value: str) -> None:
        font_family = FontFamily(value)
        self.apply_settings("font_family", font_family)

    def create_page(self, settings: SettingsDTO) -> ft.Container:
        return ft.Container(
            ft.Column(
                [
                    ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Customize how the app looks and feels"),
                    ft.Divider(height=2, color=ft.Colors.BLACK),
                    ft.Text("Theme", weight=ft.FontWeight.BOLD),
                    ft.RadioGroup(
                        content=ft.Row(
                            [
                                ft.Radio(value=ThemeMode.LIGHT.value, label="Light"),
                                ft.Radio(value=ThemeMode.DARK.value, label="Dark"),
                                ft.Radio(value=ThemeMode.SYSTEM.value, label="System"),
                            ]
                        ),
                        value=self.settings.theme_mode.value,
                        on_change=lambda e: self._apply_theme_mode(e.control.value),
                    ),
                    ft.Text("Font size", weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        value=self.settings.font_size.value,
                        options=[ft.dropdown.Option(size.value) for size in FontSize],
                        width=200,
                        on_select=lambda e: self._apply_font_size(e.control.value),
                    ),
                    ft.Text("Font family", weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        value=self.settings.font_family.value,
                        options=[ft.dropdown.Option(family.value) for family in FontFamily],
                        width=200,
                        on_select=lambda e: self._apply_font_family(e.control.value),
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            border_radius=10,
            alignment=ft.Alignment.CENTER_LEFT,
            expand=True,
        )
