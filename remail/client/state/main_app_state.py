from collections.abc import Callable
from enum import Enum
from typing import Union

from remail.client.state.observable_state import ObservableState
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO


class MainAppStateProperties(Enum):
    ACTIVE_THREAD = "active_thread"
    ACTIVE_CHATBOT = "active_chatbot"
    SEARCH_TERM = "search_term"
    DISPLAYED_MAILS = "displayed_mails"


class MainAppState(ObservableState[MainAppStateProperties]):
    def __init__(self):
        super().__init__()
        self.__selected: list[ConversationDTO | ThreadPreviewDTO] = []
        self.__selection_listeners: dict[
            ConversationDTO | ThreadPreviewDTO, Callable[[bool], None]
        ] = {}

    def toggle_selection(self, item: Union["ConversationDTO", "ThreadPreviewDTO"]) -> None:
        already_selected = item in self.__selected
        if already_selected:
            self.__selected.remove(item)
        else:
            self.__selected.append(item)

        if item in self.__selection_listeners:
            self.__selection_listeners[item](not already_selected)

    def listen_selection(
        self, item: Union["ConversationDTO", "ThreadPreviewDTO"], callback: Callable[[bool], None]
    ) -> None:
        self.__selection_listeners[item] = callback
