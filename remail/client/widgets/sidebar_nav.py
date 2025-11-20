from __future__ import annotations

import flet as ft


def nav_item(icon: str, label: str) -> ft.Column:
    """A sidebar item with an icon and text underneath."""
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
        controls=[
            ft.Icon(icon, size=26, color="blue"),
            ft.Text(label, size=12, color="blue"),
        ],
    )


class SidebarNav(ft.Container):
    """Left vertical navigation bar with icons + labels and dark blue background."""

    def __init__(self) -> None:
        super().__init__()

        # for the width and color of the widget
        self.width = 140
        #self.bgcolor = "#0f172a"  # 
        self.padding = ft.padding.only(top=20)

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
            controls=[
                nav_item(ft.icons.MAIL, "Dashboard"),
                nav_item(ft.icons.CHAT, "Conversations"),
            ],
        )
