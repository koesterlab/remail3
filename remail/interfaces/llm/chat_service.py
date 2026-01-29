from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, col, select

from remail.database import engine
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.models import ChatMessage, ChatSession, Contact, Email, Thread
from remail.utils.session_management import session


class ChatService:
    """Service for chat session persistence and thread context building."""

    def __init__(self) -> None:
        self.engine = engine

    @session
    def get_or_create_session(self, user_id: int, thread_id: int, session: Session) -> ChatSession:
        session.expire_on_commit = False
        existing = session.exec(
            select(ChatSession).where(
                (ChatSession.user_id == user_id) & (ChatSession.thread_id == thread_id)
            )
        ).first()
        if existing:
            return existing

        chat_session = ChatSession(user_id=user_id, thread_id=thread_id)
        session.add(chat_session)
        session.flush()
        return chat_session

    @session
    def save_message(
        self, session_id: int, role: LLMMessageRole, content: str, session: Session
    ) -> ChatMessage:
        session.expire_on_commit = False
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
        )
        session.add(message)
        session.flush()
        return message

    @session
    def get_session_messages(self, session_id: int, session: Session) -> list[ChatMessage]:
        session.expire_on_commit = False
        messages = session.exec(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(col(ChatMessage.timestamp))
        ).all()
        return list(messages)

    @session
    def build_thread_context(self, thread_id: int, session: Session) -> str:
        thread = session.get(Thread, thread_id)
        if not thread:
            return ""

        messages = session.exec(
            select(Email).where(Email.thread_id == thread_id).order_by(col(Email.sent_at))
        ).all()

        header = f"Thread title: {thread.title}"
        if not messages:
            return f"{header}\nMessages: (none)"

        lines = [header, "Messages:"]
        for email in messages:
            sender = session.get(Contact, email.sender_id)
            sender_name = (
                sender.name
                if sender and sender.name
                else (sender.email_address if sender else "Unknown sender")
            )
            sent_at = email.sent_at.isoformat()
            lines.append(f"- {sent_at} | {sender_name}: {email.body}")

        return "\n".join(lines)
