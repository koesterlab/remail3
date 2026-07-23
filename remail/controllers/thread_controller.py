import logging
from datetime import datetime
from types import SimpleNamespace
from typing import Any, cast

from sqlmodel import Session

from remail import errors as ee
from remail.controllers.dtos.conversations import ConversationDTO
from remail.controllers.dtos.threads import MessageContentDTO, MessageDTO, SenderDTO, ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.interfaces.email import ImapProtocol
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.thread_service import ThreadService
from remail.interfaces.email.services.user_service import UserService
from remail.models import Email
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
        self, count: int = 5, tag_id: int | None = None
    ) -> list[tuple[ThreadDTO, ConversationDTO, UserDTO]]:
        return cast(
            list[tuple[ThreadDTO, ConversationDTO, UserDTO]],
            self.service.get_most_important_threads(
                count=count,
                tag_id=tag_id,
            ),
        )

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
    def send_message(
        self, thread_id: int, message: str, attachment: list[Any], session: Session
    ) -> MessageDTO:
        """
        Sends a message to a given thread

        Args:
            thread_id: The Id of the corresponding thread
            message: The message to send
            attachment: NOT IMPLEMENTED - a list of attachments - just here to remember todo
        """
        thread = self.service.get_thread_by_id(thread_id)
        if thread is None:
            raise ValueError(f"Thread with id {thread_id} not found")
        if thread.id is None:
            raise ValueError(f"Thread with id {thread_id} has no persistent ID")
        user = thread.conversation.user
        if user is None:
            conversation_user_id = thread.conversation.user_id
            user = (
                UserService.get_user_by_id(conversation_user_id)
                if conversation_user_id is not None
                else None
            )
        if user is None:
            raise ee.NotLoggedIn("No active account is linked to this conversation")
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

        sender_contact = ContactService().get_user_contact(user)
        session.flush()
        if sender_contact.id is None:
            raise ValueError("Could not resolve sender contact for outgoing email")

        sent_at = datetime.now()
        sent_email = Email(
            body=message,
            sent_at=sent_at,
            sender_id=sender_contact.id,
            thread_id=thread.id,
            read=True,
        )
        session.add(sent_email)
        thread.last_message_time = sent_at
        session.flush()

        sender_last_name = (
            sender_contact.last_name or sender_contact.name or sender_contact.email_address
        )
        return MessageDTO(
            id=sent_email.id if sent_email.id else -1,
            sender=SenderDTO(
                id=sender_contact.id,
                first_name=sender_contact.first_name or "",
                last_name=sender_last_name,
                email=sender_contact.email_address,
            ),
            subject=thread.title,
            content=MessageContentDTO(body=message, attachments=[]),
            sent_at=sent_at,
        )
