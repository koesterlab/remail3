from collections.abc import Callable

import flet as ft

from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO

from .thread_preview import ThreadPreview
from ...state.main_app_state import MainAppState

"""
Subwidget of selectionBar to choose between different conversations of a contact
"""


class ThreadSelection(ft.Container):
    def __init__(self, state: MainAppState, on_click_back: Callable[[], None]):
        self.slided_in = False
        self.__state = state
        self.__content = ft.Column(spacing=0)
        self.__image = ft.CircleAvatar(content=ft.Text(""), bgcolor=ft.Colors.ON_SURFACE, radius=20)
        self.__primary_text = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        self.__secondary_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

        super().__init__(ft.Column(
            controls=[
                # header
                ft.Container(
                    height=100,
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda _: on_click_back()
                            ),
                            self.__image,
                            ft.Column(
                                alignment=ft.MainAxisAlignment.START,
                                controls=[self.__primary_text, self.__secondary_text],
                                spacing=6,
                            ),
                        ],
                        spacing=3,
                    ),
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
        ))

    def set_content(self, content: ConversationDTO):
        if len(content.contacts) == 1:
            contact = content.contacts[0]
            self.__image.content = (
                ft.Text(contact.first_name[0] + contact.last_name[0])
                if contact.is_known
                else ft.Icon(ft.Icons.PERSON)
            )
            self.__primary_text.value = contact.first_name + " " + contact.last_name
            self.__secondary_text.value = contact.email
        else:
            self.__image.content = ft.Icon(ft.Icons.GROUP)
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
