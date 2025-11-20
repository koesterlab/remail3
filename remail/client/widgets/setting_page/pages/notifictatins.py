import flet as ft


def create_notifications():
    return ft.Container(
        ft.Column(
            [
                ft.Text("Notifications", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Customize how and when you receive notifications"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
                ft.Row(
                    [ft.Text("Get notified on your desktop", expand=True), ft.Switch(value=True)]
                ),
                ft.Row(
                    [ft.Text("Get notified about new emails", expand=True), ft.Switch(value=True)]
                ),
                ft.Row(
                    [
                        ft.Text("No notifications between 10 PM and 8 AM", expand=True),
                        ft.Switch(value=False),
                    ]
                ),
                ft.Container(ft.ElevatedButton("Apply"), alignment=ft.alignment.center),
            ]
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
