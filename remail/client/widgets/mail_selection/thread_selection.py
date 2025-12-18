from collections.abc import Callable

import flet as ft

from remail.controllers.dtos.conversations import ConversationDTO

from ...state.main_app_state import MainAppState
from .profile_picture import create_profile_picture
from .thread_preview import ThreadPreview

"""
Subwidget of selectionBar to choose between different conversations of a contact
"""


class ThreadSelection(ft.Container):
    def __init__(self, state: MainAppState, on_click_back: Callable[[], None]):
        self.slided_in = False
        self.__state = state
        self.__content = ft.Column(spacing=0)
        self.__image = ft.Container(width=40, height=40)
        self.__primary_text = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        self.__secondary_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

        super().__init__(
            ft.Column(
                controls=[
                    # header
                    ft.Container(
                        padding=ft.padding.only(left=0, right=5, top=5, bottom=10),
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    on_click=lambda _: on_click_back(),
                                    icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                    icon_size=30,
                                ),
                                self.__image,
                                ft.Container(
                                    ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[self.__primary_text, self.__secondary_text],
                                        spacing=6,
                                    ),
                                    height=50,
                                ),
                            ],
                            spacing=7,
                        ),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY)),
                    ),
                    # thread_list
                    ft.Container(
                        alignment=ft.alignment.top_center,
                        expand=True,
                        content=ft.Column(  # outer: align content to top, middle: scroll, inner: enumeration of elements
                            scroll=ft.ScrollMode.AUTO,
                            alignment=ft.MainAxisAlignment.START,
                            spacing=0,
                            controls=[self.__content],
                        ),
                    ),
                ]
            )
        )

    def set_content(self, content: ConversationDTO):
        self.__image.content = create_profile_picture(content)
        if len(content.contacts) == 1:
            contact = content.contacts[0]
            self.__primary_text.value = contact.first_name + " " + contact.last_name
            self.__secondary_text.value = contact.email
        else:
            self.__primary_text.value = (
                content.customName
                if content.customName
                else ", ".join(
                    contact.first_name[0] + ". " + contact.last_name for contact in content.contacts
                )
            )
            self.__secondary_text.value = str(len(content.contacts)) + " Members"
        # todo: make more efficient on reload
        # todo: sort algorithm
        self.__content.controls = [ThreadPreview(elem, self.__state) for elem in content.threads]  # type: ignore
