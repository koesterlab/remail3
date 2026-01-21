from collections.abc import Callable
from enum import Enum
from typing import Union

from remail.client.state.observable_state import ObservableState
from remail.controllers import ConversationsController
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.thread_controller import ThreadController


class MainAppStateProperties(Enum):
    DRAFT = "draft"
    ACTIVE_USER = "active_user"
    ACTIVE_THREAD = "active_thread"
    ACTIVE_CONVERSATION = "active_conversation"
    ACTIVE_CHATBOT = "active_chatbot"
    SEARCH_TERM = "search_term"
    DISPLAYED_MAILS = "displayed_mails"


class MainAppState(ObservableState[MainAppStateProperties]):
    def __init__(self):
        super().__init__()
        self.__selected: list[ConversationDTO | ThreadPreviewDTO] = []
        self.__selection_listeners: dict[
            ConversationDTO | ThreadPreviewDTO | None, Callable[[bool], None]
        ] = {}

        self.conversations_controller = ConversationsController()
        self.thread_controller = ThreadController()

    def toggle_selection(self, item: Union["ConversationDTO", "ThreadPreviewDTO"]) -> None:
        already_selected = item in self.__selected
        if already_selected:
            self.__selected.remove(item)
        else:
            self.__selected.append(item)

        if item in self.__selection_listeners:
            self.__selection_listeners[item](not already_selected)
        if None in self.__selection_listeners:
            self.__selection_listeners[None](False)

    def listen_selection(
        self,
        item: Union["ConversationDTO", "ThreadPreviewDTO", None],
        callback: Callable[[bool], None],
    ) -> None:
        self.__selection_listeners[item] = callback

    def get_selected(self):
        return self.__selected

    def clear_selected(self):
        selected = self.__selected
        self.__selected = []
        for s in selected:
            if s in self.__selection_listeners:
                self.__selection_listeners[s](False)

        if None in self.__selection_listeners:
            self.__selection_listeners[None](False)
