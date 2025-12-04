from __future__ import annotations

from typing import Any

import flet as ft


class MessageBubble(ft.Container):
    """Single chat bubble (left for others, right for me)."""

    def __init__(self, message: dict[str, Any]) -> None:
        is_me = bool(message.get("is_me", False))
        text = str(message.get("text", ""))

        # --- Layout style ---
        alignment = ft.alignment.center_right if is_me else ft.alignment.center_left

        # --- Colors ---
        bgcolor = "#0069ff" if is_me else "#f3f4f6"  # for the left side, the color is shallower
        text_color = "white" if is_me else "#111111"  # deep black

        # --- Bubble style ---
        bubble = ft.Container(
            width=380,  # 400
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            border_radius=ft.border_radius.all(18),  # it would be rounder
            bgcolor=bgcolor,
            shadow=ft.BoxShadow(
                blur_radius=6,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
            ),
            content=ft.Text(
                text,
                color=text_color,
                size=15,
                weight="w400",
            ),
        )

        # --- Outer container to control alignment ---
        super().__init__(
            alignment=alignment,
            padding=ft.padding.only(left=6, right=6, top=4, bottom=4),
            content=bubble,
        )
