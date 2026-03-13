"""Service for managing threads and organizing emails."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime
from email.header import decode_header
from typing import TYPE_CHECKING

from sqlalchemy import and_, func
from sqlmodel import Session, col, desc, select

from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.database import engine
from remail.interfaces.email.services.user_service import UserService
from remail.models import Attachment, Contact, Conversation, Email, EmailReception, Thread
from remail.utils.session_management import session

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

    @session
    def get_thread_by_id(self, thread_id: int, session: Session) -> Thread | None:
        """
        Fetch a thread with all its messages.

        Args:
            thread_id: Thread ID to fetch

        Returns:
            ThreadDTO with thread data including messages, or None if not found
        """

        return session.get(Thread, thread_id)

    def create_thread(self, title: str, conversation_id: int) -> Thread:
        """
        Create a new thread.

        Args:
            title: Title of the thread
            conversation_id: Conversation ID to associate the thread with

        Returns:
            Created Thread object
        """

        new_thread = Thread(title=title, conversation_id=conversation_id)

        with Session(self.engine) as session:
            session.add(new_thread)
            session.commit()
            session.refresh(new_thread)

        return new_thread

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

    @session
    def organize_email_into_thread(
        self, email: Email, subject: str, conversation: Conversation, session: Session
    ) -> None:
        """
        Organize emails into threads within a conversation.

        Creates or updates a single thread for the conversation with all emails in chronological order.

        Args:
            email: Email to organize
            conversation: Conversation to search/create thread in
        """
        if conversation.id is None:
            return
        conversation_id = conversation.id
        try:
            subject = self.normalize_subject(subject)
            existing_thread = session.exec(
                select(Thread).where(
                    and_(
                        col(Thread.conversation_id) == conversation_id,
                        func.lower(col(Thread.title)) == subject.lower(),
                    )
                )
            ).first()

            if existing_thread:
                if email.thread_id != existing_thread.id and existing_thread.id is not None:
                    email.thread = existing_thread
                    if not email.read:
                        existing_thread.unread_count = existing_thread.unread_count + 1
                    if existing_thread.last_message_time is None:
                        existing_thread.last_message_time = email.sent_at
                    else:
                        existing_thread.last_message_time = max(
                            existing_thread.last_message_time, email.sent_at
                        )
            else:
                new_thread = Thread(
                    title=subject,
                    conversation_id=conversation.id,
                    unread_count=0 if email.read else 1,
                    last_message_time=email.sent_at,
                )

                session.add(new_thread)
                email.thread = new_thread
        except Exception as e:
            print(e)

    # from here with chatgpt
    _PREFIXES = [
        "re",
        "fw",
        "fwd",
        "fwd:",
        "fwd",
        "rv",
        "tr",
        "antwort",
        # deutsch
        "aw",
        # französisch
        "re",
        "tr",
        "r\u00e9",  # Ré:
        # spanisch / portugiesisch
        "res",
        "rsp",
        "resposta",
        "res:",
        "res",
        # italienisch
        "ris",
        "rif",
        # niederländisch
        "antw",
        "doorsturen",
        "dv",
        # skandinavisch (se/fi/no/dk)
        "sv",
        "vs",
        "vedr",
        "ang",
        "svar",
        "vid",
        "bs",
        "vb",
        # osteuropa
        "odp",
        "odp:",
        "odp",
        "odpoveď",
        "odpověď",
        "ats",
        "atb",
        # russisch
        "\u043e\u0442\u0432",  # Отв:
        "\u043f\u0435\u0440\u0435\u0441\u044b\u043b\u043a\u0430",  # Пересылка:
        # türkisch
        "yn:",
        "cevap",
        "ilet",
        "ynt",
        # arabisch (vereinfachte latinisierte Varianten)
        "rad",
        "twd",
        # chinesisch + japanisch (vereinfacht, translit.)
        "huifu",
        "转发",
        "回复",
        "答复",
        "転送",
        "返信",
    ]

    _PREFIX_REGEX = re.compile(
        r"^(?:" + r"|".join([re.escape(p) for p in _PREFIXES]) + r")\s*:\s*", re.IGNORECASE
    )

    @classmethod
    def normalize_subject(cls, subject: str) -> str:
        """
        Remove all Reply/Forward-Prefixes (RE:, AW:, Fwd:, ...),
        """
        if not subject:
            return subject
        subject = "".join(
            part.decode(enc or "utf-8") if isinstance(part, bytes) else part
            for part, enc in decode_header(subject)
        )
        cleaned = subject.strip()
        while True:
            new = cls._PREFIX_REGEX.sub("", cleaned).lstrip()
            if new == cleaned:
                break
            cleaned = new

        return cleaned.strip() or "Unparsable Subject"

    # chatgpt end

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

    @session
    def _build_thread_preview_dto(self, thread: Thread):
        unread_count = 0
        total_count = 0
        latest_message = None
        for message in thread.messages:
            if not message.read:
                unread_count += 1
            if not latest_message or message.sent_at > latest_message.sent_at:
                latest_message = message
            total_count += 1

        return ThreadPreviewDTO(
            thread_id=thread.id if thread.id is not None else -1,
            title=thread.title,
            total_count=total_count,
            unread_count=unread_count,
            last_message=latest_message.body if latest_message else "",
            last_message_datetime=latest_message.sent_at if latest_message else datetime.min,
        )

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
            subject=email.thread.title,
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

    @session
    def get_most_important_threads(
        self,
        session: Session,
        count: int = 5,
    ) -> list[tuple[ThreadDTO, ConversationDTO, UserDTO]]:
        """
        Calculates the most urgent threads from the database for all accounts
        Currently by time, later by ai

        returns: (thread_id, ConversationDTO, UserDTO)
        """
        # todo ai valuing of mails
        threads: Iterable[Thread] = session.exec(
            select(Thread)
            .order_by(
                Thread.last_message_time.desc(),  # type: ignore
            )
            .limit(count)
        )
        return [
            (
                ThreadDTO.from_model(t),
                ConversationDTO.from_model(t.conversation, t.conversation.user),
                UserService.user_to_dto(t.conversation.user),
            )
            for t in threads
        ]
