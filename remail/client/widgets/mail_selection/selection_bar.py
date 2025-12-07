import re

import flet as ft

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.conversation_selection import ConversationSelection
from remail.client.widgets.mail_selection.search_header import SearchHeader
from remail.client.widgets.mail_selection.thread_selection import ThreadSelection
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO

"""
Overall Widget to combine searchbar and selection widgets
"""


class SelectionBar(ft.Container):
    def __init__(self, state: MainAppState):
        state.register_observer(MainAppStateProperties.SEARCH_TERM, self.__on_search_change)  # type: ignore
        state.register_observer(MainAppStateProperties.DISPLAYED_MAILS, self.__set_content_to_display)  # type: ignore


        #subwidgets
        self.topic_selection = ThreadSelection(state, lambda: self.__set_content_to_display(state.get(MainAppStateProperties.DISPLAYED_MAILS)))
        self.conversation_selection = ConversationSelection(self.__on_conversation_or_action_selected, state)
        self.main_content = ft.Column(
                controls=[SearchHeader(state), self.conversation_selection],
                expand=True,
                spacing=0,
                alignment=ft.MainAxisAlignment.START,
                offset=ft.Offset(0,0),
            )
        self.topic_selection.offset = ft.Offset(1,0)
        self.topic_selection.animate_offset = 140
        self.main_content.animate_offset = 140
        self.__state = state
        self.topic_selection_active = False

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            content=ft.Stack(controls=[self.main_content, self.topic_selection],expand=True),
            expand=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        self.__set_content_to_display(state.get(MainAppStateProperties.DISPLAYED_MAILS))  # type: ignore
        self.__on_search_change("")  # initially loading data


    def __on_search_change(self, new_search_term: str | None) -> None:
        mails: list[ConversationDTO | Action] = self.__search_request(new_search_term)  # type: ignore
        if new_search_term != "" and re.match(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]", new_search_term
        ):  # option "mail hinzufügen
            mails.insert(
                0,
                Action(
                    new_search_term + " zu Kontakten hinzufügen",
                    "Als neuen Kontakt erstellen",
                    lambda: None,  # todo
                    ft.Colors.SECONDARY,
                    ft.Icons.ADD,
                ),
            )
            mails.insert(
                0,
                Action(
                    "Nachricht an " + new_search_term,
                    "Neuer Chat",
                    lambda: None,  # todo
                    ft.Colors.PRIMARY,
                    ft.Icons.MAIL,
                ),
            )

        self.__set_content_to_display(mails)

    def __on_conversation_or_action_selected(self, selected: ConversationDTO | Action) -> None:
        if isinstance(selected, ConversationDTO):
            self.__set_content_to_display([selected])
        else:
            selected.on_executed()

    def __on_topic_selected(self, selected: ThreadPreviewDTO) -> None:
        self.__state.set(MainAppStateProperties.ACTIVE_THREAD, selected)

    def __set_content_to_display(self, content_to_display: list[ConversationDTO | Action]) -> None:
        if len(content_to_display) == 1 and isinstance(content_to_display[0], ConversationDTO):
            self.__show_topic_selection(content_to_display[0])
            if not self.topic_selection_active: #slide_in_animation
                print("slide in")
                self.topic_selection.offset = ft.Offset(0,0)
                self.main_content.offset = ft.Offset(-1,0)
                self.topic_selection_active = True
        else:
            self.__show_conversation_selection(content_to_display)
            if self.topic_selection_active: # slide out animation
                print("slide out")
                self.topic_selection.offset = ft.Offset(1,0)
                self.main_content.offset = ft.Offset(0,0)
                self.topic_selection_active = False

        if self.page:
            self.update()

    def __show_conversation_selection(self, content: list[ConversationDTO | Action]) -> None:
        self.conversation_selection.set_content(content)

    def __show_topic_selection(self, conversation: ConversationDTO) -> None:
        self.topic_selection.set_content(conversation)

    def __search_request(self, searchterm: str | None = None) -> list[ConversationDTO]:
        if searchterm:
            return []  # todo request controller
        else:
            return self.__state.get(MainAppStateProperties.DISPLAYED_MAILS)
