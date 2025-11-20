import flet as ft
from remail.client.widgets.conversations_widget import ConversationsWidget


def main(page: ft.Page) -> None:
    # page.title = "ReMail"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START

    widget = ConversationsWidget()
    # widget = LoginWidget()
    # widget = SettingWidget()

    control = widget.build()

    page.add(control)


# if __name__ == "__main__":
#   ft.app(target=main)
