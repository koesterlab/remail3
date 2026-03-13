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
