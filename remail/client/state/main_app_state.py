from asyncio import Future
from collections.abc import Callable
from enum import Enum
from typing import Union

from remail.client.state.observable_state import ObservableState
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.tag_controller import TagController
from remail.controllers.thread_controller import ThreadController


class MainAppStateProperties(Enum):
    DRAFT = "draft"
    ACTIVE_USER = "active_user"
    ACTIVE_THREAD = "active_thread"
    ACTIVE_THREAD_CONVERSATION = "active_thread_conversation"
    ACTIVE_CONVERSATION = "active_conversation"
    ACTIVE_CHATBOT = "active_chatbot"
    ACTIVE_ATTACHMENTS = "active_attachments"
    ACTIVE_SETTINGS = "active_settings"
    SEARCH_TERM = "search_term"
    DISPLAYED_MAILS = "displayed_mails"
    ACCOUNTS_CHANGED = "accounts_changed"
    SORT_BY_DATE = "sort_by_date"


class MainAppState(ObservableState[MainAppStateProperties]):
    def __init__(self):
        super().__init__()
        self.__selected: list[ConversationDTO | ThreadPreviewDTO] = []
        self.__selection_listeners: dict[
            ConversationDTO | ThreadPreviewDTO | None, Callable[[bool], None]
        ] = {}

        self.thread_controller = ThreadController()
        self.tag_controller = TagController()
        self.account_controllers: dict[str, AccountController] = {}
        self.sync_threads: list[Future] = []

    def get_active_email_account(self) -> AccountController:
        mail: UserDTO | None = self.get(MainAppStateProperties.ACTIVE_USER)
        if mail is None:
            raise Exception("Account Controller was requested without active email account")
        controller = self.account_controllers.get(mail.email)
        if controller is None:
            raise Exception("Account Controller was requested but not found for mail " + mail.email)
        return controller

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
