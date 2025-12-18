"""Service for managing threads and organizing emails."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Session, col, desc, select

from remail.database import engine
from remail.models import Attachment, Contact, Email, EmailReception, Thread

if TYPE_CHECKING:
    from remail.controllers.dtos.threads import (
        MessageDTO,
        ThreadDTO,
    )


class ThreadService:
    """Service for managing email threads."""

    def __init__(self):
        """Initialize thread service."""
        self.engine = engine

    def get_thread_by_id(self, thread_id: int) -> ThreadDTO | None:
        """
        Fetch a thread with all its messages.

        Args:
            thread_id: Thread ID to fetch

        Returns:
            ThreadDTO with thread data including messages, or None if not found
        """
        with Session(self.engine) as session:
            thread = session.get(Thread, thread_id)

            if not thread:
                return None

            messages = session.exec(
                select(Email).where(Email.thread_id == thread_id).order_by(col(Email.sent_at))
            ).all()

            return self._build_thread_dto(session, thread, list(messages))

    def get_thread_for_conversation(self, conversation_id: int) -> dict | None:
        """
        Fetch the thread for a conversation with preview data.

        Args:
            conversation_id: Conversation ID to fetch thread for

        Returns:
            Thread dictionary with preview information, or None if no thread exists
        """
        with Session(self.engine) as session:
            thread = session.exec(
                select(Thread).where(Thread.conversation_id == conversation_id)
            ).first()

            if not thread:
                return None

            messages = session.exec(
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

        with Session(self.engine) as session:
            existing_thread = session.exec(
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

                session.add(new_thread)
                session.flush()  # Get the thread ID

                if new_thread.id is not None:
                    for email in emails:
                        email.thread_id = new_thread.id

            session.commit()

    def _build_thread_dto(
        self, session: Session, thread: Thread, messages: list[Email]
    ) -> ThreadDTO:
        """
        Build a complete thread DTO with all messages.

        Args:
            session: Database session
            thread: Thread model instance
            messages: List of Email model instances

        Returns:
            ThreadDTO with thread data and messages
        """
        from remail.controllers.dtos.threads import ThreadDTO

        if thread.id is None:
            raise ValueError("Thread ID cannot be None")

        # Collect all contacts from the thread (senders + recipients)
        contacts = self._collect_thread_contacts(session, messages)

        return ThreadDTO(
            id=thread.id,
            title=thread.title,
            messages=[self._build_message_dto(session, msg) for msg in messages],
            contacts=contacts,
        )

    def _collect_thread_contacts(self, session: Session, messages: list[Email]) -> list:
        """
        Collect all unique contacts involved in a thread.

        Includes senders and all recipients (TO, CC, BCC) from all emails.

        Args:
            session: Database session
            messages: List of Email model instances

        Returns:
            List of ContactDTO objects
        """
        from remail.controllers.dtos.conversations import ContactDTO

        seen_contact_ids: set[int] = set()
        contacts: list[ContactDTO] = []

        for email in messages:
            # Add sender
            if email.sender_id and email.sender_id not in seen_contact_ids:
                sender = session.get(Contact, email.sender_id)
                if sender:
                    seen_contact_ids.add(sender.id)  # type: ignore
                    contacts.append(
                        ContactDTO(
                            id=sender.id,  # type: ignore
                            first_name=sender.first_name or "",
                            last_name=sender.last_name or "",
                            email=sender.email_address,
                            is_known=sender.is_known,
                            type=sender.contact_type,
                        )
                    )

            # Add recipients
            if email.id:
                receptions = session.exec(
                    select(EmailReception).where(EmailReception.email_id == email.id)
                ).all()

                for reception in receptions:
                    if reception.contact_id not in seen_contact_ids:
                        contact = session.get(Contact, reception.contact_id)
                        if contact:
                            seen_contact_ids.add(contact.id)  # type: ignore
                            contacts.append(
                                ContactDTO(
                                    id=contact.id,  # type: ignore
                                    first_name=contact.first_name or "",
                                    last_name=contact.last_name or "",
                                    email=contact.email_address,
                                    is_known=contact.is_known,
                                    type=contact.contact_type,
                                )
                            )

        return contacts

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

    def _build_message_dto(self, session: Session, email: Email) -> MessageDTO:
        """
        Build a message DTO for thread view.

        Args:
            session: Database session
            email: Email model instance

        Returns:
            MessageDTO with email data
        """
        from remail.controllers.dtos.threads import AttachmentDTO, MessageDTO, SenderDTO
        from remail.controllers.dtos.threads.message import MessageContentDTO

        if email.id is None:
            raise ValueError("Email ID cannot be None")

        sender = session.get(Contact, email.sender_id)
        attachments = session.exec(select(Attachment).where(Attachment.email_id == email.id)).all()

        return MessageDTO(
            id=email.id,
            sender=SenderDTO(
                id=sender.id if sender else None,
                first_name=sender.first_name or "" if sender else "",
                last_name=sender.last_name or "" if sender else "",
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
