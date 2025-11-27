import flet as ft

from remail.client.state.app_state import AppState


def create_notifications_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the notifications settings view."""

    def desktop_notifications_changed(e):
        app_state.desktop_notifications = e.control.value
        page.update()

    def email_notifications_changed(e):
        app_state.email_notifications = e.control.value
        page.update()

    def quiet_hours_changed(e):
        app_state.quiet_hours = e.control.value
        page.update()

    def apply_settings(e):
        # TODO: Apply and persist notification settings
        page.update()

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
                            value=app_state.desktop_notifications,
                            on_change=desktop_notifications_changed,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.Text("Get notified about new emails", expand=True),
                        ft.Switch(
                            value=app_state.email_notifications,
                            on_change=email_notifications_changed,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.Text("No notifications between 10 PM and 8 AM", expand=True),
                        ft.Switch(
                            value=app_state.quiet_hours,
                            on_change=quiet_hours_changed,
                        ),
                    ]
                ),
                ft.Container(
                    ft.OutlinedButton("Apply", on_click=apply_settings),
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
