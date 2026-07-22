# remail/interfaces/email/services/dashboard_service.py
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlmodel import Session, col, select

from remail.controllers.dtos.conversations import ThreadPreviewDTO
from remail.database.db import engine
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.email import Email
from remail.models.thread import Thread
from remail.models.user_conversation import UserConversation


class DashboardService:
    """
    Data access layer for the Dashboard.
    We should delete this Service and redistribute functions on other services.

    Notes:
    - We do NOT have a dedicated "appointments" table in the DB yet.
    - For UI testing, we treat "appointments" as "the most recent emails".
    """

    @staticmethod
    def get_recent_emails_for_user(
        user_id: int,
        limit: int = 5,
    ) -> Sequence[tuple[Email, Contact]]:
        """
        Return recent emails visible to the given user.

        Visibility rules:
        - user -> user_conversations -> conversations -> threads -> emails

        Why the joins are written without explicit ON clauses:
        - SQLAlchemy/SQLModel can infer join paths from declared foreign keys.
        - This avoids mypy interpreting the ON clause expression as a plain bool.
        """
        with Session(engine) as session:
            stmt = (
                select(Email, Contact)
                # Email.sender_id -> Contact.id
                .join(Contact)
                # Email.thread_id -> Thread.id
                .join(Thread)
                # Thread.conversation_id -> Conversation.id
                .join(Conversation)
                # UserConversation.conversation_id -> Conversation.id
                .join(UserConversation)
                .where(UserConversation.user_id == user_id)
                .order_by(col(Email.sent_at).desc())
                .limit(limit)
            )
            return session.exec(stmt).all()

    @staticmethod
    def get_unread_emails_for_user(
        user_id: int,
        limit: int = 10,
    ) -> list[dict[str, object]]:
        """Return the user's unread (and not deleted) emails, newest first."""
        with Session(engine) as session:
            stmt = (
                select(Email, Contact, Thread)
                .join(Contact)  # Email.sender_id -> Contact.id
                .join(Thread)  # Email.thread_id -> Thread.id
                .join(Conversation)  # Thread.conversation_id -> Conversation.id
                .where(Conversation.user_id == user_id)
                .where(col(Email.read).is_(False))
                .where(col(Email.deleted).is_(False))
                .order_by(col(Email.sent_at).desc())
                .limit(limit)
            )
            rows = session.exec(stmt).all()
            return [
                {
                    "sender": contact.name or contact.email_address,
                    "title": thread.title or "(no subject)",
                    "body": email.body or "",
                    "sent_at": email.sent_at,
                }
                for email, contact, thread in rows
            ]

    @staticmethod
    def get_recent_appointment_items_for_user(
        user_id: int,
        limit: int = 3,
    ) -> Sequence[tuple[ThreadPreviewDTO, datetime]]:
        """
        Temporary appointments source for UI testing:
        Just reuse the most recent emails.

        Later, when a real appointments/calendar table exists, replace this logic.
        """
        return []
