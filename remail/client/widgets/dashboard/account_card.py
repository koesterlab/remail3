# remail/client/widgets/dashboard/account_card.py
from __future__ import annotations

from typing import Any

import flet as ft

AccountDict = dict[str, Any]


class AccountCard(ft.Container):


    def __init__(self, account: AccountDict) -> None:
        email: str = account.get("email", "")
        label: str = account.get("label", "Active")
        color = account.get("color", ft.Colors.PRIMARY)

        icon_container = ft.Container(
            width=42,
            height=42,
            bgcolor=color,
            border_radius=21,
            alignment=ft.alignment.center,
            content=ft.Icon(
                ft.Icons.EMAIL,
                color=ft.Colors.ON_PRIMARY,
                size=22,
            ),
        )

        text_column = ft.Column(
            spacing=4,
            controls=[
                ft.Text(
                    email,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Text(
                    label,
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
        )

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            padding=ft.padding.all(16),
            border_radius=18,
            expand=True,
            content=ft.Row(
                controls=[icon_container, text_column],
                spacing=16,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
