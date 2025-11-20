import flet as ft


def create_archived():
    return ft.Container(
        ft.Column(
            [
                ft.Text("Archived Items", weight=ft.FontWeight.BOLD),
                ft.Text("View and manage your archived email and conversations"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
            ]
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
