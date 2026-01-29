import re

import flet as ft

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.conversation_selection import ConversationSelection
from remail.client.widgets.mail_selection.search_header import SearchHeader
from remail.client.widgets.mail_selection.thread_selection import ThreadSelection
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import MessageDTO

"""
Overall Widget to combine searchbar and selection widgets
"""


class SelectionBar(ft.Container):
    def __init__(self, state: MainAppState):
        state.register_observer(MainAppStateProperties.SEARCH_TERM, self.__on_search_change)  # type: ignore
        state.register_observer(
            MainAppStateProperties.DISPLAYED_MAILS, self.__set_content_to_display
        )  # type: ignore

        # subwidgets
        self.topic_selection = ThreadSelection(state, self._deselect_conversation)
        self.conversation_selection = ConversationSelection(
            self.__on_conversation_or_action_selected, state
        )
        self.main_content = ft.Column(
            controls=[SearchHeader(state), self.conversation_selection],
            expand=True,
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            offset=ft.Offset(0, 0),
        )
        self.topic_selection.offset = ft.Offset(1, 0)
        self.topic_selection.animate_offset = 140
        self.main_content.animate_offset = 140
        self.__state = state
        self.topic_selection_active = False

        # state
        self.selected_conversation: ConversationDTO | None = None
        self.search_elements: list[
            tuple[ConversationDTO, ThreadPreviewDTO, MessageDTO] | Action
        ] = []

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            content=ft.Stack(controls=[self.main_content, self.topic_selection], expand=True),
            expand=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        state.register_observer(MainAppStateProperties.DISPLAYED_MAILS, lambda _: self._re_render())
        self._re_render()  # type: ignore
        self.__on_search_change("")  # initially loading data

    def _deselect_conversation(self):
        self.selected_conversation = None
        self._re_render()

    def __on_search_change(self, new_search_term: str) -> None:
        if new_search_term.strip() == "":
            self.search_elements = []
            self._re_render()
            return

        mails: list[tuple[ConversationDTO, ThreadPreviewDTO, MessageDTO] | Action] = (
            self.__search_request(new_search_term)
        )
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

        self.search_elements = mails
        self._re_render()

    def _re_render(self):
        if self.selected_conversation:  # sub-navigation
            self.__set_content_to_display([self.selected_conversation])
        elif self.search_elements:  # search todo: show sub-elements (thread, message)
            self.__set_content_to_display(
                [e[0] if isinstance(e, tuple) else e for e in self.search_elements]
            )
        else:  # default: show inbox conversations
            self.__set_content_to_display(self.__state.get(MainAppStateProperties.DISPLAYED_MAILS))

    def __on_conversation_or_action_selected(self, selected: ConversationDTO | Action) -> None:
        print(selected)
        if isinstance(selected, ConversationDTO):
            self.selected_conversation = selected
            self._re_render()
        else:
            selected.on_executed()

    def __on_topic_selected(self, selected: ThreadPreviewDTO) -> None:
        self.__state.set(MainAppStateProperties.ACTIVE_THREAD, selected)
        self.__state.set(MainAppStateProperties.ACTIVE_CONVERSATION, self.selected_conversation)

    def __set_content_to_display(self, content_to_display: list[ConversationDTO | Action]) -> None:
        if len(content_to_display) == 1 and isinstance(content_to_display[0], ConversationDTO):
            self.__show_topic_selection(content_to_display[0])
            if not self.topic_selection_active:  # slide_in_animation
                self.topic_selection.offset = ft.Offset(0, 0)
                self.main_content.offset = ft.Offset(-1, 0)
                self.topic_selection_active = True
        else:
            self.__show_conversation_selection(content_to_display)
            if self.topic_selection_active:  # slide out animation
                self.topic_selection.offset = ft.Offset(1, 0)
                self.main_content.offset = ft.Offset(0, 0)
                self.topic_selection_active = False
        if self.page:
            try:
                self.update()
            except Exception as e:
                print(e)

    def __show_conversation_selection(self, content: list[ConversationDTO | Action]) -> None:
        self.conversation_selection.set_content(content)

    def __show_topic_selection(self, conversation: ConversationDTO) -> None:
        self.topic_selection.set_content(conversation)

    def __search_request(
        self, searchterm: str
    ) -> list[tuple[ConversationDTO, ThreadPreviewDTO, MessageDTO] | Action]:
        return []  # todo request controller
