import flet as ft

from remail.enums import Language, Timezone

from .settings_sub_view import SettingsSubView


class LanguageView(SettingsSubView):
    def create_page(self, settings) -> ft.Container:
        self.settings = self.controller.get_settings()
        return ft.Container(
            ft.Column(
                [
                    ft.Text("Language & Region", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Choose your preferred language for the application"),
                    ft.Divider(height=2, color=ft.Colors.BLACK),
                    ft.Text("Application Language", weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        value=settings.language.value,
                        options=[ft.dropdown.Option(lang.value) for lang in Language],
                        expand=True,
                        on_select=lambda e: self.apply_settings(
                            "language", Language(e.control.value)
                        ),
                    ),
                    ft.Text("Timezone", weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        value=settings.timezone.value,
                        options=[ft.dropdown.Option(tz.value) for tz in Timezone],
                        expand=True,
                        on_select=lambda e: self.apply_settings(
                            "timezone", Timezone(e.control.value)
                        ),
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
