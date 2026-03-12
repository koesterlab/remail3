from typing import Any

from remail.controllers.dtos.conversations import ConversationDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.interfaces.email import ImapProtocol
from remail.interfaces.email.services.thread_service import ThreadService
from remail.utils.session_management import session


class ThreadController:
    """Controller for thread operations."""

    def __init__(self):
        """Initialize thread controller."""

        self.service = ThreadService()

    @session
    def get_thread(self, thread_id: int) -> ThreadDTO | None:
        """
        Fetch a complete thread with all messages.

        Args:
            thread_id: Thread ID to fetch

        Returns:
            ThreadDTO with thread data, or None if not found
        """

        res = self.service.get_thread_by_id(thread_id)
        if res:
            return ThreadDTO.from_model(res)
        return None

    def get_most_urgent_threads(
        self, count: int = 5
    ) -> list[tuple[ThreadDTO, ConversationDTO, UserDTO]]:
        return self.service.get_most_important_threads(count=count)  # type:ignore

    @session
    def create_thread(self, conversation_id, name: str)->ThreadDTO:
        """
        Creates a thread in the local database. Note that it is only "synced" with other clients if a mail is sent

        Args:
              conversation_id: The Id of the conversation the thread belongs to
              name: Name of the new thread
        """

        return ThreadDTO.from_model(self.service.create_thread(name, conversation_id))

    @session
    def send_message(self, thread_id, message: str, attachment: list[Any]):
        """
        Sends a message to a given thread

        Args:
            thread_id: The Id of the corresponding thread
            message: The message to send
            attachment: NOT IMPLEMENTED - a list of attachments - just here to remember todo
        """
        thread = self.service.get_thread_by_id(thread_id)
        user = thread.conversation.users[0]
        protocol = ImapProtocol(serialized=user.connection)
        protocol.send_email(
            sender=(user.name, user.email),
            recipients=[(c.first_name + " " + c.last_name, c.email) for c in thread.contacts],
            subject=("Re: " if thread.messages else "") + thread.title,
            msg=message
        )
