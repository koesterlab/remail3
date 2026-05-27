import flet as ft


def create_croppable_email_address(email: str, size: int, color: ft.Colors) -> ft.Container:
    parts = email.split("@")
    if len(parts) == 2:
        (name, host) = parts
        return ft.Container(
            ft.Row(
                [
                    ft.Text(
                        name,
                        expand=True,
                        text_align=ft.TextAlign.END,
                        size=size,
                        color=color,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text("@" + host, size=size, color=color),
                ],
                expand=True,
                spacing=0,
                alignment=ft.MainAxisAlignment.END,
            ),
            expand=True,
        )
    return ft.Container(ft.Text(email, size=size, color=color))
