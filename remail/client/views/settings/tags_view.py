import flet as ft

from remail.controllers.tag_controller import TagController
from remail.models import Tag

_TAG_COLORS: dict[str, str] = {
    "Work": ft.Colors.BLUE,
    "Personal": ft.Colors.GREEN,
    "Urgent": ft.Colors.RED,
    "Newsletter": ft.Colors.ORANGE,
    "Finance": ft.Colors.PURPLE,
}


def _tag_chip(name: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(name, size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
        bgcolor=_TAG_COLORS.get(name, ft.Colors.TEAL),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


class TagsView(ft.Container):
    def __init__(self) -> None:
        super().__init__(expand=True, padding=20)
        self.tag_controller = TagController()
        self.name_input = ft.TextField(label="Tag name", width=220)
        self.description_input = ft.TextField(label="Description", expand=True)
        self._rebuild()

    def _rebuild(self) -> None:
        tags = self.tag_controller.get_all_tags()

        def refresh() -> None:
            self._rebuild()
            try:
                self.update()
            except RuntimeError:
                pass

        self.content = ft.Column(
            spacing=16,
            controls=[
                ft.Text("Tags", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        self.name_input,
                        self.description_input,
                        ft.FilledButton(
                            "Add",
                            icon=ft.Icons.ADD,
                            on_click=lambda _: self._add_tag(refresh),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
                ft.Column(
                    spacing=8,
                    controls=[self._tag_row(tag, refresh) for tag in tags],
                ),
            ],
        )

    def _add_tag(self, refresh) -> None:
        self.tag_controller.create_tag(
            self.name_input.value or "",
            self.description_input.value or "",
        )
        self.name_input.value = ""
        self.description_input.value = ""
        refresh()

    def _tag_row(self, tag: Tag, refresh) -> ft.Container:
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            content=ft.Row(
                controls=[
                    _tag_chip(tag.name),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                tag.description or "No description",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Delete tag",
                        on_click=lambda _, tag_id=tag.id: self._delete_tag(tag_id, refresh),
                    ),
                ],
            ),
        )

    def _delete_tag(self, tag_id: int | None, refresh) -> None:
        if tag_id is None:
            return
        self.tag_controller.delete_tag(tag_id)
        refresh()
