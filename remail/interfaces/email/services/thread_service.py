"""Service for managing threads and organizing emails."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, col, desc, select

from remail.controllers.dtos.threads import (
    AttachmentDTO,
    MessageDTO,
    SenderDTO,
    ThreadDTO,
)
from remail.controllers.dtos.threads.message import MessageContentDTO
from remail.models import Attachment, Contact, Email, Thread


class ThreadService:
    """Service for managing email threads."""

    def __init__(self):
        """Initialize thread service."""
        self.session = Session()

    def get_thread_by_id(self, thread_id: int) -> ThreadDTO | None:
        """
        Fetch a thread with all its messages.

        Args:
            thread_id: Thread ID to fetch

        Returns:
            ThreadDTO with thread data including messages, or None if not found
        """
        thread = self.session.get(Thread, thread_id)

        if not thread:
            return None

        messages = self.session.exec(
            select(Email).where(Email.thread_id == thread_id).order_by(col(Email.sent_at))
        ).all()

        return self._build_thread_dto(thread, list(messages))

    def get_thread_for_conversation(self, conversation_id: int) -> dict | None:
        """
        Fetch the thread for a conversation with preview data.

        Args:
            conversation_id: Conversation ID to fetch thread for

        Returns:
            Thread dictionary with preview information, or None if no thread exists
        """
        thread = self.session.exec(
            select(Thread).where(Thread.conversation_id == conversation_id)
        ).first()

        if not thread:
            return None

        messages = self.session.exec(
            select(Email).where(Email.thread_id == thread.id).order_by(desc(Email.sent_at))
        ).all()

        if not messages:
            return None

        return self._build_thread_preview_dict(thread, list(messages))

    def organize_emails_into_threads(self, emails: list[Email], conversation_id: int) -> None:
        """
        Organize emails into threads within a conversation.

        Creates or updates a single thread for the conversation with all emails in chronological order.

        Args:
            emails: List of Email objects to organize
            conversation_id: Conversation ID to create thread for
        """

        if not emails:
            return

        existing_thread = self.session.exec(
            select(Thread).where(Thread.conversation_id == conversation_id)
        ).first()

        if existing_thread:
            for email in emails:
                if email.thread_id != existing_thread.id and existing_thread.id is not None:
                    email.thread_id = existing_thread.id
        else:
            thread_title = emails[0].subject

            new_thread = Thread(
                title=thread_title,
                conversation_id=conversation_id,
            )

            self.session.add(new_thread)
            self.session.flush()  # Get the thread ID

            if new_thread.id is not None:
                for email in emails:
                    email.thread_id = new_thread.id

        self.session.commit()

    def _build_thread_dto(self, thread: Thread, messages: list[Email]) -> ThreadDTO:
        """
        Build a complete thread DTO with all messages.

        Args:
            thread: Thread model instance
            messages: List of Email model instances

        Returns:
            ThreadDTO with thread data and messages
        """
        if thread.id is None:
            raise ValueError("Thread ID cannot be None")

        return ThreadDTO(
            id=thread.id,
            title=thread.title,
            messages=[self._build_message_dto(msg) for msg in messages],
        )

    def _build_thread_preview_dict(self, thread: Thread, messages: list[Email]) -> dict:
        """
        Build a thread preview dictionary for conversation listings.

        Args:
            thread: Thread model instance
            messages: List of Email model instances (should be ordered by sent_at desc)

        Returns:
            Dictionary with thread preview data
        """
        last_message = messages[0] if messages else None

        return {
            "thread_id": thread.id,
            "title": thread.title,
            "total_count": len(messages),
            "unread_count": 0,  # TODO: Implement unread tracking -- Later Feature
            "last_message": last_message.body[:100] if last_message else "",
            "last_message_datetime": (last_message.sent_at if last_message else datetime.now()),
        }

    def _build_message_dto(self, email: Email) -> MessageDTO:
        """
        Build a message DTO for thread view.

        Args:
            email: Email model instance

        Returns:
            MessageDTO with email data
        """
        if email.id is None:
            raise ValueError("Email ID cannot be None")

        sender = self.session.get(Contact, email.sender_id)
        attachments = self.session.exec(
            select(Attachment).where(Attachment.email_id == email.id)
        ).all()

        return MessageDTO(
            id=email.id,
            sender=SenderDTO(
                id=sender.id if sender else None,
                first_name=sender.first_name if sender else "",
                last_name=sender.last_name if sender else "",
                email=sender.email_address if sender else "",
            ),
            subject=email.subject,
            content=MessageContentDTO(
                body=email.body,
                attachments=[
                    AttachmentDTO(
                        file_name=att.filename,
                        file_size=0,  # TODO: Add file size to Attachment model -- Later Feature
                        file_type="application/octet-stream",  # TODO: Add file type -- Later Feature
                        url=f"/attachments/{att.id}",  # Placeholder URL -- Later Feature
                    )
                    for att in attachments
                ],
            ),
            sent_at=email.sent_at,
        )
