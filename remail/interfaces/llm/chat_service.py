"""Service for managing persisted chat sessions and messages."""

from __future__ import annotations

from sqlalchemy import delete
from sqlmodel import Session, col, select

from remail.database import engine
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.models import ChatMessage, ChatSession, Contact, Email, Thread


class ChatService:
    """Service for chat session persistence and thread context building."""

    def __init__(self) -> None:
        """Initialize chat service."""

        self.engine = engine

    def get_or_create_session(self, user_id: int, thread_id: int) -> ChatSession:
        """
        Get an existing chat session for a user and thread or create a new one.

        Args:
            user_id: User ID for the session
            thread_id: Thread ID for the session

        Returns:
            ChatSession instance
        """

        if user_id is None or thread_id is None:
            raise ValueError("user_id and thread_id are required")

        with Session(self.engine) as session:
            chat_session = session.exec(
                select(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.thread_id == thread_id,
                )
            ).first()

            if chat_session:
                return chat_session

            chat_session = ChatSession(user_id=user_id, thread_id=thread_id)
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            return chat_session

    def build_thread_context(self, thread_id: int) -> str:
        """
        Build thread context from emails for prompt injection.

        Args:
            thread_id: Thread ID to fetch emails for

        Returns:
            Formatted thread context string
        """

        if thread_id is None:
            return ""

        with Session(self.engine) as session:
            thread = session.get(Thread, thread_id)

            if not thread:
                return ""

            emails = session.exec(
                select(Email, Contact)
                .join(Contact, col(Contact.id) == Email.sender_id)
                .where(Email.thread_id == thread_id)
                .order_by(col(Email.sent_at))
            ).all()

            lines = [f"Thread title: {thread.title}"]

            if not emails:
                lines.append("No emails found for this thread.")
                return "\n".join(lines)

            lines.append("Thread emails:")

            for email, sender in emails:
                sender_name = self._format_sender_name(sender)
                lines.append(f"- From: {sender_name} <{sender.email_address}>")
                lines.append(f"  Sent: {email.sent_at.isoformat()}")
                lines.append(f"  Subject: {email.subject}")
                lines.append("  Body:")
                lines.append(self._indent_block(email.body, 4))

            return "\n".join(lines)

    def save_message(
        self, session_id: int, role: LLMMessageRole | str, content: str
    ) -> ChatMessage:
        """
        Persist a chat message to the database.

        Args:
            session_id: Chat session ID
            role: Message role (user/assistant/etc)
            content: Message content

        Returns:
            Saved ChatMessage instance
        """

        if isinstance(role, str):
            role = LLMMessageRole(role)

        new_message = ChatMessage(session_id=session_id, role=role, content=content)

        with Session(self.engine) as session:
            session.add(new_message)
            session.commit()
            session.refresh(new_message)
            return new_message

    def get_session_messages(self, session_id: int) -> list[LLMMessage]:
        """
        Fetch session messages in chronological order.

        Args:
            session_id: Chat session ID

        Returns:
            List of LLMMessage instances
        """

        with Session(self.engine) as session:
            messages = session.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(col(ChatMessage.created_at), col(ChatMessage.id))
            ).all()

            return [LLMMessage(role=message.role, content=message.content) for message in messages]

    def clear_session_messages(self, session_id: int) -> None:
        """
        Delete all messages for a chat session.

        Args:
            session_id: Chat session ID
        """

        with Session(self.engine) as session:
            session.exec(delete(ChatMessage).where(col(ChatMessage.session_id) == session_id))
            session.commit()

    @staticmethod
    def _format_sender_name(sender: Contact) -> str:
        name_parts = [sender.first_name or "", sender.last_name or ""]
        full_name = " ".join(part for part in name_parts if part).strip()
        return full_name or sender.name or sender.email_address

    @staticmethod
    def _indent_block(text: str, spaces: int) -> str:
        prefix = " " * spaces
        return "\n".join(f"{prefix}{line}" for line in text.splitlines())
