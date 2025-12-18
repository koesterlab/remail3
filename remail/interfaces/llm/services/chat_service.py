"""Chat service for managing chat sessions and messages with thread context."""

from datetime import datetime

from sqlmodel import Session, select

from remail.models import ChatMessage, ChatSession, Email


class ChatService:
    """Service for managing chat sessions and messages linked to email threads."""

    def __init__(self, session: Session):
        """Initialize ChatService with a database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def get_or_create_session(self, user_id: int, thread_id: int) -> ChatSession:
        """Get existing chat session for user+thread or create new one.

        Args:
            user_id: ID of the user
            thread_id: ID of the email thread

        Returns:
            ChatSession instance (existing or newly created)
        """
        # Try to find existing session
        statement = select(ChatSession).where(
            (ChatSession.user_id == user_id) & (ChatSession.thread_id == thread_id)
        )
        existing_session = self.session.exec(statement).first()

        if existing_session:
            return existing_session

        # Create new session
        new_session = ChatSession(user_id=user_id, thread_id=thread_id)
        self.session.add(new_session)
        self.session.commit()
        self.session.refresh(new_session)

        return new_session

    def build_thread_context(self, thread_id: int) -> str:
        """Build formatted context string from all emails in a thread.

        Args:
            thread_id: ID of the email thread

        Returns:
            Formatted string containing all email content in the thread
        """
        # Query all emails in the thread
        statement = select(Email).where(Email.id == thread_id)
        emails = self.session.exec(statement).all()

        if not emails:
            return ""

        context_lines = ["Thread context:", ""]

        for email in emails:
            sender_name = email.sender.name if email.sender else "Unknown"
            sender_email = email.sender.email_address if email.sender else "unknown@example.com"
            recipients_str = ", ".join(
                [f"{r.contact.name} ({r.contact.email_address})" for r in email.recipients]
                if email.recipients
                else []
            )

            context_lines.append(f"From: {sender_name} <{sender_email}>")
            if recipients_str:
                context_lines.append(f"To: {recipients_str}")
            context_lines.append(f"Date: {email.sent_at.isoformat() if email.sent_at else 'Unknown'}")
            context_lines.append(f"Subject: {email.subject}")
            context_lines.append("")
            context_lines.append(email.body)
            context_lines.append("-" * 80)
            context_lines.append("")

        return "\n".join(context_lines)

    def save_message(
        self, session_id: int, role: str, content: str
    ) -> ChatMessage:
        """Save a message to a chat session.

        Args:
            session_id: ID of the chat session
            role: Message role ('user' or 'assistant')
            content: Message content

        Returns:
            ChatMessage instance
        """
        message = ChatMessage(session_id=session_id, role=role, content=content)
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        return message

    def get_session_messages(self, session_id: int) -> list[ChatMessage]:
        """Get all messages in a chat session.

        Args:
            session_id: ID of the chat session

        Returns:
            List of ChatMessage instances ordered by creation time
        """
        statement = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
        return self.session.exec(statement).all()

    def update_session_timestamp(self, session_id: int) -> None:
        """Update the updated_at timestamp for a session.

        Args:
            session_id: ID of the chat session
        """
        statement = select(ChatSession).where(ChatSession.id == session_id)
        session = self.session.exec(statement).first()

        if session:
            session.updated_at = datetime.now()
            self.session.add(session)
            self.session.commit()
