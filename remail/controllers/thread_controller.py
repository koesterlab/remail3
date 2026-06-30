import logging
from types import SimpleNamespace
from typing import Any

from remail.controllers.dtos.conversations import ConversationDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.interfaces.email import ImapProtocol
from remail.interfaces.email.services.thread_service import ThreadService
from remail.utils.session_management import session
from remail.utils.timer import Timer

_logger = logging.getLogger(__name__)


class ThreadController:
    """Controller for thread operations."""

    def __init__(self):
        """Initialize thread controller."""

        self.service = ThreadService()

    @session
    def get_thread(self, thread_id: int) -> ThreadDTO | None:
        _logger.info("Loading thread %d from DB...", thread_id)
        t = Timer()
        res = self.service.get_thread_by_id(thread_id)
        if res:
            dto = ThreadDTO.from_model(res)
            _logger.info(
                "Thread %d loaded: %d message(s). (%s)", thread_id, len(dto.messages), t.elapsed()
            )
            return dto
        return None

    def get_most_urgent_threads(
        self, count: int = 5
    ) -> list[tuple[ThreadDTO, ConversationDTO, UserDTO]]:
        return self.service.get_most_important_threads(count=count)  # type:ignore

    @session
    def create_thread(self, conversation_id: int, name: str) -> ThreadDTO:
        """
        Creates a thread in the local database. Note that it is only "synced" with other clients if a mail is sent

        Args:
              conversation_id: The Id of the conversation the thread belongs to
              name: Name of the new thread

        Returns:
              ThreadDTO with the created thread data
        """

        return ThreadDTO.from_model(self.service.create_thread(name, conversation_id))

    @session
    def send_message(self, thread_id: int, message: str, attachment: list[Any]) -> None:
        """
        Sends a message to a given thread

        Args:
            thread_id: The Id of the corresponding thread
            message: The message to send
            attachment: NOT IMPLEMENTED - a list of attachments - just here to remember todo
        """
        thread = self.service.get_thread_by_id(thread_id)
        user = thread.conversation.user
        protocol = ImapProtocol(serialized=user.connection)
        subject = ("Re: " if thread.messages else "") + thread.title
        mail = SimpleNamespace(
            thread=SimpleNamespace(
                title=subject,
                conversation=thread.conversation,
            ),
            body=message,
            attachments=[],
        )
        protocol.send_email(mail)
