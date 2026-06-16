"""Tag settings view."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from remail.client.views.settings.settings_sub_view import SettingsSubView
from remail.controllers.dtos import SettingsDTO
from remail.controllers.tag_controller import TagController
from remail.models import Tag

_TAG_COLORS: dict[str, str] = {
    "Work": ft.Colors.BLUE,
    "Personal": ft.Colors.GREEN,
    "Urgent": ft.Colors.RED,
    "Newsletter": ft.Colors.ORANGE,
    "Finance": ft.Colors.PURPLE,
}
_FALLBACK_COLORS = (ft.Colors.TEAL, ft.Colors.CYAN, ft.Colors.INDIGO, ft.Colors.BROWN)


class TagsView(SettingsSubView):
    """Settings page for creating and deleting email tags."""

    def __init__(self) -> None:
        self.tag_controller = TagController()
        super().__init__()

    def create_page(self, settings: SettingsDTO) -> ft.Container:
        name_input = ft.TextField(label="Tag name", width=220)
        description_input = ft.TextField(label="Description", width=360)

        def refresh() -> None:
            self.content = self.create_page(self.settings)
            if self.page:
                self.update()

        def add_tag(_: ft.ControlEvent) -> None:
            name = name_input.value.strip() if name_input.value else ""
            description = description_input.value.strip() if description_input.value else None
            if not name:
                return
            self.tag_controller.create_tag(name, description)
            refresh()

        tags = self.tag_controller.get_all_tags()

        return ft.Container(
            ft.Column(
                [
                    ft.Text("Tags", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Create labels that can be assigned to saved emails"),
                    ft.Divider(height=2, color=ft.Colors.BLACK),
                    ft.Column(
                        controls=[
                            self._tag_row(tag, index, refresh) for index, tag in enumerate(tags)
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1),
                    ft.Text("Add tag", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            name_input,
                            description_input,
                            ft.FilledButton("Add Tag", icon=ft.Icons.ADD, on_click=add_tag),
                        ],
                        spacing=12,
                        wrap=True,
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            border_radius=10,
            alignment=ft.Alignment.CENTER_LEFT,
            expand=True,
        )

    def _tag_row(self, tag: Tag, index: int, refresh: Callable[[], None]) -> ft.Row:
        def delete_tag(_: ft.ControlEvent) -> None:
            if tag.id is None:
                return
            self.tag_controller.delete_tag(tag.id)
            refresh()

        return ft.Row(
            [
                _tag_chip(tag.name, index),
                ft.Text(tag.description or "", expand=True, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.ERROR,
                    tooltip="Delete tag",
                    on_click=delete_tag,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )


def _tag_chip(name: str, index: int) -> ft.Container:
    return ft.Container(
        content=ft.Text(name, size=12, color=ft.Colors.WHITE),
        bgcolor=_tag_color(name, index),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        width=110,
    )


def _tag_color(name: str, index: int = 0) -> str:
    return _TAG_COLORS.get(name, _FALLBACK_COLORS[index % len(_FALLBACK_COLORS)])
