"""Service for managing persistent chat sessions for threads."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from remail.database import engine
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.models import ChatMessage, ChatSession, Contact, Email, Thread


class ChatService:
    """Service for chat persistence and thread context building."""

    def __init__(self) -> None:
        self.engine = engine

    def get_or_create_session(self, user_id: int, thread_id: int) -> ChatSession:
        """Get or create a chat session for a user and thread."""
        with Session(self.engine) as session:
            existing = session.exec(
                select(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.thread_id == thread_id,
                )
            ).first()

            if existing:
                return existing

            new_session = ChatSession(user_id=user_id, thread_id=thread_id)
            session.add(new_session)
            session.commit()
            session.refresh(new_session)
            return new_session

    def build_thread_context(self, thread_id: int) -> str:
        """Build a formatted thread context for LLM prompts."""
        with Session(self.engine) as session:
            thread = session.get(Thread, thread_id)
            if not thread:
                return ""

            emails = session.exec(
                select(Email).where(Email.thread_id == thread_id).order_by(Email.sent_at)
            ).all()

            if not emails:
                return f'Thread "{thread.title}" has no messages.'

            lines: list[str] = [f'Thread "{thread.title}" emails:']

            for index, email in enumerate(emails, start=1):
                sender = session.get(Contact, email.sender_id)
                sender_label = sender.email_address if sender else "Unknown sender"
                lines.append(f"{index}. From: {sender_label} | Sent: {email.sent_at.isoformat()}")
                if email.subject:
                    lines.append(f"Subject: {email.subject}")
                if email.body:
                    lines.append("Body:")
                    lines.append(email.body.strip())
                lines.append("---")

            return "\n".join(lines)

    def save_message(
        self,
        session_id: int,
        role: LLMMessageRole,
        content: str,
        created_at: datetime | None = None,
    ) -> ChatMessage:
        """Persist a chat message."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            created_at=created_at or datetime.utcnow(),
        )
        with Session(self.engine) as session:
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    def get_session_messages(self, session_id: int) -> list[ChatMessage]:
        """Fetch all messages for a session ordered by creation time."""
        with Session(self.engine) as session:
            messages = session.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at)
            ).all()
            return list(messages)
