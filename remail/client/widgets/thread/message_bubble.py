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
        alignment = ft.alignment.center_right if is_me else ft.alignment.center_left

        # --- Bubble style ---
        own_border = ft.border_radius.only(top_left=18, bottom_left=18, bottom_right=18)
        others_border = ft.border_radius.only(top_right=18, bottom_left=18, bottom_right=18)
        bubble = ft.Container(
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            border_radius=own_border if is_me else others_border,  # it would be rounder
            bgcolor=ft.Colors.PRIMARY if is_me else ft.Colors.SECONDARY,
            shadow=ft.BoxShadow(
                blur_radius=6,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
            ),
            content=ft.Text(
                message.content,
                color=ft.Colors.ON_PRIMARY if is_me else ft.Colors.ON_SECONDARY,
                size=15,
                weight=ft.FontWeight.W_400,
            ),
        )

        # --- Outer container to control alignment ---
        super().__init__(
            alignment=alignment,
            padding=ft.padding.only(left=6, right=6, top=4, bottom=4),
            content=bubble if is_me else ft.Row([create_contact_picture(message.sender), bubble]),
        )
