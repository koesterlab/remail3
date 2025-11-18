import flet as ft

def main(page: ft.Page):
    page.title = "Remail 2.0"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(main)