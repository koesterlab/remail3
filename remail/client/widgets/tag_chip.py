import flet as ft

TAG_COLORS: dict[str, str] = {
    "Work": ft.Colors.BLUE,
    "Personal": ft.Colors.GREEN,
    "Urgent": ft.Colors.RED,
    "Newsletter": ft.Colors.ORANGE,
    "Spam": ft.Colors.BROWN,
}


def tag_color(name: str) -> str:
    return TAG_COLORS.get(name, ft.Colors.TEAL)


def tag_chip(name: str, compact: bool = False) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            name,
            size=11 if compact else 12,
            weight=ft.FontWeight.W_500 if compact else ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
            no_wrap=True,
        ),
        bgcolor=tag_color(name),
        border_radius=8 if compact else 16,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3)
        if compact
        else ft.Padding.symmetric(horizontal=12, vertical=5),
    )
