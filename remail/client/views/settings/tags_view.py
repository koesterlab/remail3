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
        content=ft.Text(
            name,
            size=12,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
            no_wrap=True,
        ),
        bgcolor=_TAG_COLORS.get(name, ft.Colors.TEAL),
        border_radius=16,
        padding=ft.Padding.symmetric(horizontal=12, vertical=5),
    )


def _tag_count_badge(count: int) -> ft.Container:
    label = "tag" if count == 1 else "tags"
    return ft.Container(
        content=ft.Text(
            f"{count} {label}",
            size=12,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.PRIMARY,
        ),
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
        border_radius=16,
        padding=ft.Padding.symmetric(horizontal=12, vertical=6),
    )


class TagsView(ft.Container):
    def __init__(self) -> None:
        super().__init__(expand=True, padding=20)
        self.tag_controller = TagController()
        self.name_input = ft.TextField(
            label="Tag name",
            hint_text="Project",
            prefix_icon=ft.Icons.LABEL_OUTLINE,
            width=220,
            dense=True,
            on_submit=lambda _: self._add_tag(),
        )
        self.description_input = ft.TextField(
            label="Description",
            hint_text="Project related emails",
            prefix_icon=ft.Icons.NOTES_OUTLINED,
            expand=True,
            dense=True,
            on_submit=lambda _: self._add_tag(),
        )
        self.status_text = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT, visible=False)
        self._rebuild()

    def _rebuild(self) -> None:
        tags = self.tag_controller.get_all_tags()

        self.content = ft.Column(
            spacing=16,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            expand=True,
                            spacing=4,
                            controls=[
                                ft.Text("Tags", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "Create reusable labels for emails and future AI suggestions.",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                        ),
                        _tag_count_badge(len(tags)),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self._form_panel(),
                self.status_text,
                ft.Column(
                    spacing=10,
                    controls=[self._tag_row(tag) for tag in tags] or [self._empty_state()],
                ),
            ],
        )

    def _form_panel(self) -> ft.Container:
        return ft.Container(
            padding=12,
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            content=ft.Row(
                controls=[
                    self.name_input,
                    self.description_input,
                    ft.FilledButton(
                        "Add tag",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: self._add_tag(),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
        )

    def _refresh(self) -> None:
        self._rebuild()
        try:
            self.update()
        except RuntimeError:
            pass

    def _set_status(self, message: str, color: str = ft.Colors.ON_SURFACE_VARIANT) -> None:
        self.status_text.value = message
        self.status_text.color = color
        self.status_text.visible = True

    def _add_tag(self) -> None:
        try:
            tag = self.tag_controller.create_tag(
                self.name_input.value or "",
                self.description_input.value or "",
            )
        except ValueError:
            self._set_status("Enter a tag name before adding it.", ft.Colors.ERROR)
            self._refresh()
            return

        self.name_input.value = ""
        self.description_input.value = ""
        self._set_status(f'"{tag.name}" is saved.', ft.Colors.PRIMARY)
        self._refresh()

    def _tag_row(self, tag: Tag) -> ft.Container:
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.LABEL, color=_TAG_COLORS.get(tag.name, ft.Colors.TEAL), size=20
                    ),
                    _tag_chip(tag.name),
                    ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            ft.Text(
                                tag.description or "No description",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.ERROR,
                        tooltip="Delete tag",
                        on_click=lambda _, tag_id=tag.id: self._delete_tag(tag_id),
                    ),
                ],
            ),
        )

    @staticmethod
    def _empty_state() -> ft.Container:
        return ft.Container(
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("No tags yet", color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                spacing=10,
            ),
        )

    def _delete_tag(self, tag_id: int | None) -> None:
        if tag_id is None:
            return
        self.tag_controller.delete_tag(tag_id)
        self._set_status("Tag deleted.", ft.Colors.ON_SURFACE_VARIANT)
        self._refresh()
