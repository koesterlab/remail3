import flet as ft

from remail.client.views.settings.settings_sub_view import SettingsSubView
from remail.controllers.dtos import SettingsDTO


class NotificationsView(SettingsSubView):
    def create_page(self, settings: SettingsDTO) -> ft.Container:
        return ft.Container(
            ft.Column(
                [
                    ft.Text("Notifications", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Customize how and when you receive notifications"),
                    ft.Divider(height=2, color=ft.Colors.BLACK),
                    ft.Row(
                        [
                            ft.Text("Get notified on your desktop", expand=True),
                            ft.Switch(
                                value=settings.desktop_notifications,
                                on_change=lambda e: self.apply_settings(
                                    "desktop_notifications", e.control.value
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Get notified about new emails", expand=True),
                            ft.Switch(
                                value=settings.email_notifications,
                                on_change=lambda e: self.apply_settings(
                                    "email_notifications", e.control.value
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("No notifications between 10 PM and 8 AM", expand=True),
                            ft.Switch(
                                value=settings.quiet_hours,
                                on_change=lambda e: self.apply_settings(
                                    "quiet_hours", e.control.value
                                ),
                            ),
                        ]
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
