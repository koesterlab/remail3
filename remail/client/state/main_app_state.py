from asyncio import Future
from collections.abc import Callable
from enum import Enum
from typing import Union

from remail.client.state.observable_state import ObservableState
from remail.client.state.task_progress import TaskProgress
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.thread_controller import ThreadController


class MainAppStateProperties(Enum):
    DRAFT = "draft"
    ACTIVE_USER = "active_user"
    ACTIVE_THREAD = "active_thread"
    ACTIVE_THREAD_CONVERSATION = "active_thread_conversation"
    ACTIVE_CONVERSATION = "active_conversation"
    ACTIVE_CHATBOT = "active_chatbot"
    ACTIVE_SETTINGS = "active_settings"
    SEARCH_TERM = "search_term"
    DISPLAYED_MAILS = "displayed_mails"
    ACCOUNTS_CHANGED = "accounts_changed"
    RUNNING_TASKS = "running_tasks"


class MainAppState(ObservableState[MainAppStateProperties]):
    def __init__(self):
        super().__init__()
        self.__selected: list[ConversationDTO | ThreadPreviewDTO] = []
        self.__selection_listeners: dict[
            ConversationDTO | ThreadPreviewDTO | None, Callable[[bool], None]
        ] = {}

        self.thread_controller = ThreadController()
        self.account_controllers: dict[str, AccountController] = {}
        self.sync_threads: list[Future] = []

        # Seed the running-tasks dict so observers never receive None.
        self._values[MainAppStateProperties.RUNNING_TASKS] = {}

    # ------------------------------------------------------------------ #
    # Task-tray helpers
    # ------------------------------------------------------------------ #

    def report_task(self, task_id: str, message: str, progress: float | None = None) -> None:
        """Add or update a task entry in the tray (upsert).

        This is the primary method for background processes to report progress.
        Its signature matches the :attr:`~AccountController.progress_callback`
        contract directly, so it can be passed as-is::

            acc.set_callback_progress(state.report_task)

        Args:
            task_id: Stable identifier for this task (e.g. ``"sync-user@example.com"``).
                     Chosen by the caller; must be unique across concurrent tasks.
            message: Human-readable status string displayed in the tray.
            progress: Completion fraction ``[0.0, 1.0]``, or ``None`` for indeterminate.
        """
        tasks: dict[str, TaskProgress] = self._values[MainAppStateProperties.RUNNING_TASKS]
        if task_id in tasks:
            tasks[task_id].message = message
            tasks[task_id].progress = progress
        else:
            tasks[task_id] = TaskProgress(task_id, message, progress)
        self.trigger(MainAppStateProperties.RUNNING_TASKS)

    def remove_task(self, task_id: str) -> None:
        """Remove a finished task from the task tray.

        No-ops silently when ``task_id`` is not found.

        Args:
            task_id: Identifier of the task to remove.
        """
        tasks: dict[str, TaskProgress] = self._values[MainAppStateProperties.RUNNING_TASKS]
        if task_id not in tasks:
            return
        del tasks[task_id]
        self.trigger(MainAppStateProperties.RUNNING_TASKS)

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
