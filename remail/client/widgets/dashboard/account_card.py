# remail/client/widgets/dashboard/account_card.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.widgets.dashboard.croppable_email_adress import create_croppable_email_address
from remail.controllers.dtos.user_dto import UserDTO

AccountDict = dict[str, Any]


class AccountCard(ft.Container):
    def __init__(self, account: UserDTO) -> None:
        icon_container = ft.Stack(
            [
                ft.CircleAvatar(ft.Icon(ft.Icons.MAIL, size=18), width=35, height=35),
                ft.Container(
                    ft.Row(
                        [
                            ft.Text(
                                str(account.unread_conversations), color=ft.Colors.WHITE, size=11
                            ),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    offset=ft.Offset(1.32, 0.001),
                    bgcolor=ft.Colors.DEEP_ORANGE_900,
                    border_radius=30,
                    padding=ft.padding.all(0),
                    width=15,
                    height=15,
                    visible=account.unread_conversations > 0,
                ),
            ]
        )

        text_column = ft.Column(
            spacing=4,
            controls=[
                create_croppable_email_address(account.email, 13, ft.Colors.ON_SURFACE),
                ft.Text(
                    account.name,
                    size=10,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            expand=True,
        )

        super().__init__(
            border_radius=3,
            expand=True,
            padding=2,
            content=ft.Row(
                controls=[icon_container, text_column],
                spacing=16,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
