"""Main entry point for the Remail client application."""

import logging

import flet as ft

from remail.client.views.index_view import IndexView

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

application_page: ft.Page | None = None


def main(page: ft.Page):
    """Initialize and run the Remail application.

    Args:
        page: The Flet page object
    """
    global application_page
    application_page = page
    page.title = "Remail 2.0"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    view = IndexView()
    page.add(view)
    view.start()


if __name__ == "__main__":
    ft.context.disable_auto_update()
    ft.run(main)


def show_snack_bar(elem: ft.Control, **kwargs):
    global application_page
    if not application_page:
        return
    application_page.show_dialog(ft.SnackBar(elem, **kwargs))


def update_page():
    global application_page
    if not application_page:
        return
    application_page.update()
