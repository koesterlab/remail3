from __future__ import annotations

import flet as ft

from remail.client.widgets.mail_selection.profile_picture import (
    create_contact_picture,
)
from remail.controllers.dtos.conversations import ContactDTO
from remail.controllers.dtos.threads import MessageDTO


class MessageBubble(ft.Container):
    """Single chat bubble (left for others, right for me)."""

    def __init__(self, message: MessageDTO, current_user: ContactDTO) -> None:
        is_me = message.sender == current_user

        # --- Layout style ---
        alignment = ft.Alignment.CENTER_RIGHT if is_me else ft.Alignment.CENTER_LEFT
        row_alignment = ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START

        # --- Date/time label ---
        formatted_time = message.sent_at.strftime("%b %d, %Y  %H:%M")
        date_label = ft.Text(
            formatted_time,
            size=11,
            color=ft.Colors.OUTLINE,
            italic=True,
        )

           # --- Attachments ---
        attachment_chips: list[ft.Control] = []
        for att in message.content.attachments:
            attachment_chips.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ATTACHMENT, size=14),
                            ft.Text(att.file_name, size=12, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=4,
                        tight=True,
                    ),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=ft.BorderRadius.all(8),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    margin=ft.Margin.only(top=4),
                )
            )

        # --- Bubble body ---
        own_border = ft.BorderRadius.only(top_left=18, bottom_left=18, bottom_right=18)
        others_border = ft.BorderRadius.only(top_right=18, bottom_left=18, bottom_right=18)

        bubble_content: list[ft.Control] = [
            ft.Text(
                message.content.body,
                color=ft.Colors.ON_SURFACE,
                size=15,
                weight=ft.FontWeight.W_400,
                selectable=True,
            )
        ]

        if attachment_chips:
            bubble_content.append(ft.Column(attachment_chips, spacing=0, tight=True))

        bubble = ft.Container(
            margin=ft.Margin.only(left=20) if is_me else ft.Margin.only(right=20),
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border_radius=own_border if is_me else others_border,
            bgcolor=ft.Colors.SURFACE,
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=6,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
            ),
            content=ft.Column(bubble_content, spacing=6, tight=True),
        )
        # --- Row with optional avatar ---
        bubble_row = bubble if is_me else ft.Row([create_contact_picture(message.sender), bubble])

        # --- Outer container to control alignment ---
        super().__init__(
            alignment=alignment,
            padding=ft.Padding.only(left=6, right=6, top=4, bottom=4),
            content=ft.Column(
                [
                    bubble_row,
                    ft.Row([date_label], alignment=row_alignment),
                ],
                spacing=2,
                tight=True,
            ),
            expand=True,
        )
