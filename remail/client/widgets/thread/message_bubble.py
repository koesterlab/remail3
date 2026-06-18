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

        # --- Bubble style ---
        own_border = ft.BorderRadius.only(top_left=18, bottom_left=18, bottom_right=18)
        others_border = ft.BorderRadius.only(top_right=18, bottom_left=18, bottom_right=18)
        text_color = ft.Colors.ON_PRIMARY if is_me else ft.Colors.ON_SECONDARY
        bubble_content: list[ft.Control] = [
            ft.Text(
                message.content.body.strip(),
                color=text_color,
                size=15,
                weight=ft.FontWeight.W_400,
            )
        ]
        if message.content.attachments:
            bubble_content.append(self._build_attachments(message, text_color))

        bubble = ft.Container(
            margin=ft.Margin.only(left=20) if is_me else ft.Margin.only(right=20),
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border_radius=own_border if is_me else others_border,  # it would be rounder
            bgcolor=ft.Colors.PRIMARY if is_me else ft.Colors.SECONDARY,
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=6,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
            ),
            content=ft.Column(bubble_content, spacing=8, tight=True),
        )

        # --- Outer container to control alignment ---
        super().__init__(
            alignment=alignment,
            padding=ft.Padding.only(left=6, right=6, top=4, bottom=4),
            content=bubble if is_me else ft.Row([create_contact_picture(message.sender), bubble]),
        )

    @staticmethod
    def _build_attachments(message: MessageDTO, text_color: str) -> ft.Control:
        controls: list[ft.Control] = []
        for attachment in message.content.attachments:
            if attachment.file_type.startswith("image/") and attachment.url:
                controls.append(
                    ft.Container(
                        border_radius=6,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Image(
                            src=attachment.url,
                            width=260,
                            height=160,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                    )
                )
            controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.ATTACH_FILE, size=16, color=text_color),
                        ft.Text(
                            attachment.file_name,
                            color=text_color,
                            size=12,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            expand=True,
                        ),
                    ],
                    spacing=6,
                )
            )
        return ft.Column(controls, spacing=6, tight=True)
