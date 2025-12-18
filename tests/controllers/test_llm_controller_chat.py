"""Integration tests for LLMController with chat functionality."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from sqlmodel import Session

from remail.controllers.llm_controller import LLMController
from remail.interfaces.llm.response import LLMCompletionResponse, LLMCompletionChoice, LLMCompletionMessage
from remail.models import Contact, Email, User


def create_mock_response(text: str) -> LLMCompletionResponse:
    """Create a mock LLMCompletionResponse with the given text."""
    choice = LLMCompletionChoice(
        index=0,
        message=LLMCompletionMessage(role="assistant", content=text),
        finish_reason="stop",
    )
    return LLMCompletionResponse(
        id="test-id",
        object="chat.completion",
        created=1234567890,
        model="llama",
        choices=[choice],
    )


@pytest.fixture
def user(session: Session) -> User:
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        password="hashedpassword123",
        protocol="IMAP",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def contact(session: Session) -> Contact:
    """Create a test contact."""
    contact = Contact(name="Sender", email_address="sender@example.com")
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@pytest.fixture
def email(session: Session, contact: Contact) -> Email:
    """Create a test email."""
    email = Email(
        subject="Project Proposal",
        body="Here is the project proposal with all the details...",
        sent_at=datetime.now(UTC),
        sender_id=contact.id,
    )
    session.add(email)
    session.commit()
    session.refresh(email)
    return email


@pytest.fixture
def llm_controller_with_db(session: Session) -> LLMController:
    """Create an LLMController with database session."""
    with patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    }):
        return LLMController(db_session=session)


class TestLLMControllerChat:
    """Test suite for LLMController chat functionality."""

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_with_thread_context_success(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test successful chat with thread context."""
        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            return_value=create_mock_response("This proposal looks great!"),
        ):
            result = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="What do you think about this proposal?",
            )

        assert result["status"] == "success"
        assert "session_id" in result
        assert result["completion"] == "This proposal looks great!"
        assert "response" in result

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_creates_session(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test that chat creates a new session."""
        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            return_value=create_mock_response("Response"),
        ):
            result = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="Hello",
            )

        assert result["status"] == "success"
        session_id = result["session_id"]

        # Verify session exists in database
        from remail.models import ChatSession
        from sqlmodel import select
        
        statement = select(ChatSession).where(ChatSession.id == session_id)
        db_session = session.exec(statement).first()
        
        assert db_session is not None
        assert db_session.user_id == user.id
        assert db_session.thread_id == email.id

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_persists_messages(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test that chat messages are persisted."""
        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            return_value=create_mock_response("This is the assistant's response."),
        ):
            result = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="Tell me about the proposal",
            )

        assert result["status"] == "success"
        session_id = result["session_id"]

        # Verify messages are saved
        from remail.models import ChatMessage
        from sqlmodel import select
        
        statement = select(ChatMessage).where(ChatMessage.session_id == session_id)
        messages = session.exec(statement).all()

        # Should have user message and assistant response
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Tell me about the proposal"
        assert messages[1].role == "assistant"
        assert messages[1].content == "This is the assistant's response."

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_multiple_turns_same_session(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test multiple chat turns in same session."""
        responses = [
            create_mock_response("First response"),
            create_mock_response("Second response"),
        ]

        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            side_effect=responses,
        ):
            result1 = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="First question",
            )

            session_id = result1["session_id"]

            result2 = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="Second question",
            )

        assert result2["session_id"] == session_id

        # Verify all messages are in same session
        from remail.models import ChatMessage
        from sqlmodel import select
        
        statement = select(ChatMessage).where(ChatMessage.session_id == session_id)
        messages = session.exec(statement).all()

        assert len(messages) == 4  # 2 user + 2 assistant
        assert messages[0].content == "First question"
        assert messages[1].content == "First response"
        assert messages[2].content == "Second question"
        assert messages[3].content == "Second response"

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_includes_thread_context(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test that thread context is injected into prompt."""
        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            return_value=create_mock_response("Response"),
        ) as mock_gen:
            llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="What about this?",
            )

        # Verify thread context was included in the prompt
        call_args = mock_gen.call_args
        prompt = call_args.kwargs.get("prompt") or call_args.args[0]

        assert "Thread context:" in prompt
        assert email.subject in prompt
        assert email.body in prompt

    def test_chat_without_db_session(self):
        """Test chat fails gracefully without database session."""
        with patch.dict("os.environ", {
            "LLM_API_KEY": "test-key",
            "LLM_BASE_URL": "https://test.example.com",
        }):
            controller = LLMController(db_session=None)

            result = controller.chat_with_thread_context(
                user_id=1,
                thread_id=1,
                user_message="Hello",
            )

            assert result["status"] == "error"
            assert "not available" in result["message"]

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_custom_system_prompt(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test chat with custom system prompt."""
        custom_prompt = "You are an expert email analyst."

        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            return_value=create_mock_response("Response"),
        ):
            result = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="Analyze this",
                system_prompt=custom_prompt,
            )

        assert result["status"] == "success"

    @patch.dict("os.environ", {
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "https://test.example.com",
    })
    def test_chat_error_handling(
        self, llm_controller_with_db: LLMController, user: User, email: Email, session: Session
    ):
        """Test error handling in chat."""
        with patch.object(
            llm_controller_with_db.service,
            "generate_completion",
            side_effect=Exception("API error"),
        ):
            result = llm_controller_with_db.chat_with_thread_context(
                user_id=user.id,
                thread_id=email.id,
                user_message="Hello",
            )

        assert result["status"] == "error"
        assert "Chat generation failed" in result["message"]
