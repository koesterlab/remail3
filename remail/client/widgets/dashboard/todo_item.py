# remail/client/widgets/dashboard/todo_item.py
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import flet as ft

from remail.client.state import MainAppState
from remail.client.widgets.dashboard.croppable_email_adress import create_croppable_email_address
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO

TodoDict = dict[str, Any]

_TAG_COLORS: dict[str, str] = {
    "Work": ft.Colors.BLUE,
    "Urgent": ft.Colors.RED,
    "Newsletter": ft.Colors.ORANGE,
    "Finance": ft.Colors.PURPLE,
}


def _tag_chip(name: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(name, size=11, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
        bgcolor=_TAG_COLORS.get(name, ft.Colors.TEAL),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
    )


def _preview_tags(title: str, body: str, sent_at: datetime) -> list[str]:
    text = f"{title} {body}".casefold()
    tags: list[str] = []

    if any(keyword in text for keyword in ["newsletter", "jackpot", "rabatt", "aktion"]):
        tags.append("Newsletter")
    if any(keyword in text for keyword in ["invoice", "rechnung", "bank", "finance"]):
        tags.append("Finance")
    if (datetime.now() - sent_at).days >= 3:
        tags.append("Urgent")
    if not tags:
        tags.append("Work")

    return tags[:2]


class TodoItem(ft.Container):
    def __init__(self, state: MainAppState, thread: ThreadDTO, account: UserDTO) -> None:
        todo = thread.messages[0]
        top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    value=thread.title,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                ),
                ft.Container(
                    bgcolor=ft.Colors.ERROR,
                    border_radius=8,
                    padding=ft.Padding.all(2),
                    content=ft.Text(
                        self.fmt_badge(todo.sent_at),
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )

        meta_row = ft.Text(
            value=(
                todo.sender.first_name.strip() + " " + todo.sender.last_name.strip()
                if todo.sender.first_name or todo.sender.last_name
                else todo.sender.email
            )
            + ": "
            + re.sub(r"\s+", " ", todo.content.body).strip(),
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        tags_row = ft.Row(
            controls=[
                _tag_chip(tag)
                for tag in _preview_tags(thread.title, todo.content.body, todo.sent_at)
            ],
            spacing=6,
            wrap=True,
        )

        quick_reply = ft.Container(
            margin=ft.Margin.only(top=8),
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=20,
            bgcolor=ft.Colors.SURFACE,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.CHAT_BUBBLE_OUTLINE,
                        size=16,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Text(
                        "Quick Reply",
                        size=13,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.ON_SURFACE,
                    ),
                ],
            ),
        )

        bottom_row = ft.Row(
            [
                quick_reply,
                create_croppable_email_address(account.email, 10, ft.Colors.ON_SURFACE_VARIANT),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        content_column = ft.Column(
            spacing=6,
            controls=[
                top_row,
                meta_row,
                tags_row,
                bottom_row,
            ],
        )

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            padding=ft.Padding.all(15),
            border_radius=16,
            margin=ft.Margin.only(bottom=12),
            content=content_column,
        )

    @staticmethod
    def fmt_badge(dt: datetime) -> str:
        """
        Return compact badges like '2h', '1d', '5m', '30s' (always "time ago").
        """
        now = datetime.now()
        delta = now - dt

        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "seconds ago"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h"
        days = hours // 24
        if days == 1:
            return "yesterday"
        return f"{days}d"
