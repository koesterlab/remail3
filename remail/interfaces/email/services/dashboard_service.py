# remail/interfaces/email/services/dashboard_service.py
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import desc
from sqlmodel import Session, select

from remail.database.db import engine
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.email import Email
from remail.models.thread import Thread
from remail.models.user_conversation import UserConversation


class DashboardService:
    """
    Data access layer for the Dashboard.

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
        """
        with Session(engine) as session:
            stmt = (
                select(Email, Contact)
                .join(Contact, Contact.id == Email.sender_id)
                .join(Thread, Thread.id == Email.thread_id)
                .join(Conversation, Conversation.id == Thread.conversation_id)
                .join(UserConversation, UserConversation.conversation_id == Conversation.id)
                .where(UserConversation.user_id == user_id)
                .order_by(desc(Email.sent_at))
                .limit(limit)
            )
            return session.exec(stmt).all()

    @staticmethod
    def get_recent_appointment_items_for_user(
        user_id: int,
        limit: int = 3,
    ) -> Sequence[tuple[Email, Contact]]:
        """
        Temporary appointments source for UI testing:
        Just reuse the most recent emails.

        Later, when a real appointments/calendar table exists, replace this logic.
        """
        return DashboardService.get_recent_emails_for_user(user_id=user_id, limit=limit)
