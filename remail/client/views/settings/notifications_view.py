import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers import SettingsController


def create_notifications_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the notifications settings view."""

    controller = SettingsController()
    current_settings = controller.get_settings()

    # Load current notification settings if available
    if current_settings:
        app_state.desktop_notifications = current_settings.desktop_notifications
        app_state.email_notifications = current_settings.email_notifications
        app_state.quiet_hours = current_settings.quiet_hours

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
        # Save all notification settings to database
        controller.update_settings(
            desktop_notifications=app_state.desktop_notifications,
            email_notifications=app_state.email_notifications,
            quiet_hours=app_state.quiet_hours,
        )

        # Show success message
        snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully"),
            bgcolor=ft.Colors.GREEN,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True

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
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
        expand=True,
    )
