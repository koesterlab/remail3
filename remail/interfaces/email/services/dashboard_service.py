# remail/interfaces/email/services/dashboard_service.py
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TypedDict

from sqlmodel import Session, col, select

from remail.database.db import engine
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.email import Email
from remail.models.thread import Thread
from remail.models.user_conversation import UserConversation


class DashboardEmailRow(TypedDict):
    sent_at: datetime
    subject: str


def _subject_from_thread_or_body(thread_title: str | None, body: str) -> str:
    if thread_title and thread_title.strip():
        return thread_title.strip()

    # fallback: first non-empty line from body
    for line in (body or "").splitlines():
        if line.strip():
            return line.strip()[:80]

    return "(no subject)"


class DashboardService:
    """
    Data access layer for the Dashboard.

    Notes:
    - No dedicated appointments table yet.
    - We return "dashboard rows" with precomputed subject to avoid ORM lazy loading
      outside a session.
    """

    @staticmethod
    def get_recent_emails_for_user(
        user_id: int,
        limit: int = 5,
    ) -> Sequence[tuple[DashboardEmailRow, Contact]]:
        """
        Return recent emails visible to the given user.

        IMPORTANT:
        - Do NOT return ORM Email objects that require lazy-loading (e.g., email.thread)
          outside the session context.
        - Instead, select the fields we need (Email.sent_at, Email.body, Thread.title)
          and build a small dict for the view.
        """
        with Session(engine) as session:
            stmt = (
                select(Email.sent_at, Email.body, Thread.title, Contact)
                .join(Contact)  # Email.sender_id -> Contact.id
                .join(Thread)  # Email.thread_id -> Thread.id
                .join(Conversation)  # Thread.conversation_id -> Conversation.id
                .join(UserConversation)  # UserConversation.conversation_id -> Conversation.id
                .where(UserConversation.user_id == user_id)
                .order_by(col(Email.sent_at).desc())
                .limit(limit)
            )

            rows = session.exec(stmt).all()

            out: list[tuple[DashboardEmailRow, Contact]] = []
            for sent_at, body, thread_title, sender in rows:
                out.append(
                    (
                        {
                            "sent_at": sent_at,
                            "subject": _subject_from_thread_or_body(thread_title, body),
                        },
                        sender,
                    )
                )
            return out

    @staticmethod
    def get_recent_appointment_items_for_user(
        user_id: int,
        limit: int = 3,
    ) -> Sequence[tuple[DashboardEmailRow, Contact]]:
        """
        Temporary appointments source for UI testing: reuse recent emails.
        """
        return DashboardService.get_recent_emails_for_user(user_id=user_id, limit=limit)
