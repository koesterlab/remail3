from collections.abc import Callable

import flet as ft

from remail.client.state.main_app_state import MainAppState
from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.action_preview import ActionPreview
from remail.client.widgets.mail_selection.contact_preview import ContactPreview
from remail.client.widgets.mail_selection.group_preview import GroupPreview
from remail.controllers.dtos.conversations import ConversationDTO

"""
Subwidget of selectionBar to choose between different contacts (+groups) and actions
"""


class ConversationSelection(ft.Container):
    def __init__(self, callback: Callable[[Action | ConversationDTO], None], state: MainAppState):
        self.callback = callback
        self.content = ft.Column(spacing=0)
        super().__init__(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(  # outer: align content to top, middle: scroll, inner: enumeration of elements
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.START,
                spacing=0,
                controls=[self.content],
            ),
        )

    def set_content(self, content: list[ConversationDTO | Action]):
        # todo: make more efficient on reload
        # todo: sort algorithm

        def create_list_item(elem: Action | ConversationDTO):
            def callback():
                self.callback(elem)

            if isinstance(elem, Action):
                item = ActionPreview(elem, callback)
            elif len(elem.contacts) == 1:
                item = ContactPreview(elem, callback)
            else:
                item = GroupPreview(elem, callback)

            return item

        self.content.controls = [create_list_item(elem) for elem in content]
