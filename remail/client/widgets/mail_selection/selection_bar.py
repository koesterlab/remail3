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
        self.main_content = ft.AnimatedSwitcher(
            ft.Container(),
            expand=True,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=130,
            switch_in_curve=ft.AnimationCurve.LINEAR,
            switch_out_curve=ft.AnimationCurve.LINEAR,
        )
        self.__state = state
        self.conversation_selection = ConversationSelection(
            self.__on_conversation_or_action_selected, state
        )
        self.topic_selection = ThreadSelection(state, lambda: self.__set_content_to_display(state.get(MainAppStateProperties.DISPLAYED_MAILS)))

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            content=ft.Column(
                controls=[SearchHeader(state), self.main_content],
                expand=True,
                spacing=0,
                alignment=ft.MainAxisAlignment.START,
            ),
            expand=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        state.register_observer(MainAppStateProperties.SEARCH_TERM, self.__on_search_change) #type: ignore
        state.register_observer(MainAppStateProperties.DISPLAYED_MAILS, self.__set_content_to_display)  # type: ignore
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
        else:
            self.__show_conversation_selection(content_to_display)

        if self.page:
            self.main_content.update()

    def __show_conversation_selection(self, content: list[ConversationDTO | Action]) -> None:
        self.conversation_selection.set_content(content)
        self.main_content.content = self.conversation_selection

    def __show_topic_selection(self, conversation: ConversationDTO) -> None:
        self.topic_selection.set_content(conversation)
        self.main_content.content = self.topic_selection

    def __search_request(self, searchterm: str | None = None) -> list[ConversationDTO]:
        if searchterm:
            return []  # todo request controller
        else:
            return self.__state.get(MainAppStateProperties.DISPLAYED_MAILS)
