"""Tests for EmailController."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from remail import errors as ee
from remail.controllers.email_controller import EmailController
from remail.enums import RecipientKind
from remail.models import Contact, Email


@pytest.fixture
def mock_protocol():
    """Create a mock ImapProtocol."""

    with patch("remail.controllers.email_controller.ImapProtocol") as mock:
        protocol_instance = MagicMock()
        protocol_instance.user_username = "user@example.com"
        protocol_instance.logged_in = False
        mock.return_value = protocol_instance

        yield protocol_instance


@pytest.fixture
def controller(mock_protocol):
    """Create an EmailController instance with mocked protocol."""

    return EmailController(
        username="user@example.com",
        password="password123",
        host="imap.example.com",
    )


class TestLogin:
    """Tests for login functionality."""

    def test_login_success(self, controller, mock_protocol):
        """Test successful login."""

        mock_protocol.login.return_value = None

        result = controller.login()

        assert result["status"] == "success"
        assert result["message"] == "Successfully logged in"
        assert result["logged_in"] is True

        mock_protocol.login.assert_called_once()

    def test_login_invalid_credentials(self, controller, mock_protocol):
        """Test login with invalid credentials."""

        mock_protocol.login.side_effect = ee.InvalidLoginData()

        result = controller.login()

        assert result["status"] == "error"
        assert result["message"] == "Invalid login credentials"
        assert result["logged_in"] is False


class TestFromId:
    """Tests for loading an EmailController from a saved user."""

    def test_from_id_uses_persisted_host(self):
        """Test that from_id uses the stored host value."""
        mock_user = MagicMock()
        mock_user.id = 7
        mock_user.email = "user@example.com"
        mock_user.password = "secret"
        mock_user.host = "imap.example.com"

        with patch("remail.controllers.email_controller.UserService") as mock_user_service:
            with patch("remail.controllers.email_controller.ImapProtocol") as mock_protocol:
                mock_user_service.get_all_users.return_value = [mock_user]

                EmailController.from_id(7)

                mock_protocol.assert_called_once_with(
                    username="user@example.com",
                    password="secret",
                    host="imap.example.com",
                )

    def test_login_generic_error(self, controller, mock_protocol):
        """Test login with generic error."""

        mock_protocol.login.side_effect = Exception("Connection timeout")

        result = controller.login()

        assert result["status"] == "error"
        assert "Login failed" in result["message"]
        assert "Connection timeout" in result["message"]
        assert result["logged_in"] is False


class TestLogout:
    """Tests for logout functionality."""

    def test_logout_success(self, controller, mock_protocol):
        """Test successful logout."""

        mock_protocol.logout.return_value = None

        result = controller.logout()

        assert result["status"] == "success"
        assert result["message"] == "Successfully logged out"
        assert result["logged_in"] is False

        mock_protocol.logout.assert_called_once()

    def test_logout_with_error(self, controller, mock_protocol):
        """Test logout with error."""

        mock_protocol.logout.side_effect = Exception("Logout error")

        result = controller.logout()

        assert result["status"] == "error"
        assert "Logout failed" in result["message"]
        assert result["logged_in"] is False


class TestSendEmail:
    """Tests for send email functionality."""

    def test_send_email_success(self, controller, mock_protocol):
        """Test successful email sending."""

        mock_protocol.send_email.return_value = None

        thread_stub = SimpleNamespace(contacts=[SimpleNamespace(email="recipient@example.com")])

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = thread_stub

            result = controller.send_email(
                subject="Test Subject",
                body="Test Body",
                thread_id=123,
            )

        assert result["status"] == "success"
        assert result["message"] == "Email sent successfully"
        assert "email" in result

        mock_protocol.send_email.assert_called_once()

    def test_send_email_uses_thread_contacts(self, controller, mock_protocol):
        """Test sending email uses recipients from thread contacts."""

        mock_protocol.send_email.return_value = None

        thread_stub = SimpleNamespace(
            contacts=[
                SimpleNamespace(email="to1@example.com"),
                SimpleNamespace(email="to2@example.com"),
            ]
        )

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = thread_stub

            result = controller.send_email(
                subject="Test",
                body="Body",
                thread_id=42,
            )

        assert result["status"] == "success"

        call_args = mock_protocol.send_email.call_args
        email_arg = call_args[0][0]

        assert email_arg.subject == "Test"
        assert email_arg.body == "Body"
        assert len(email_arg.recipients) == 2

        kinds = {rec.kind for rec in email_arg.recipients}

        assert kinds == {RecipientKind.TO}

    def test_send_email_with_attachments(self, controller, mock_protocol):
        """Test sending email with attachments."""

        mock_protocol.send_email.return_value = None

        thread_stub = SimpleNamespace(contacts=[SimpleNamespace(email="to@example.com")])

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = thread_stub

            result = controller.send_email(
                subject="Test",
                body="Body",
                attachments=["file1.pdf", "file2.jpg"],
                thread_id=5,
            )

        assert result["status"] == "success"

        call_args = mock_protocol.send_email.call_args
        email_arg = call_args[0][0]

        assert len(email_arg.attachments) == 2
        assert email_arg.attachments[0].filename == "file1.pdf"
        assert email_arg.attachments[1].filename == "file2.jpg"

    def test_send_email_not_logged_in(self, controller, mock_protocol):
        """Test sending email when not logged in."""

        mock_protocol.send_email.side_effect = ee.NotLoggedIn()

        thread_stub = SimpleNamespace(contacts=[SimpleNamespace(email="to@example.com")])

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = thread_stub

            result = controller.send_email(
                subject="Test",
                body="Body",
                thread_id=7,
            )

        assert result["status"] == "error"
        assert result["message"] == "Not logged in"

    def test_send_email_value_error(self, controller, mock_protocol):
        """Test sending email returns ValueError message."""

        mock_protocol.send_email.side_effect = ValueError("No recipients provided.")

        thread_stub = SimpleNamespace(contacts=[SimpleNamespace(email="to@example.com")])

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = thread_stub

            result = controller.send_email(
                subject="Test",
                body="Body",
                thread_id=9,
            )

        assert result["status"] == "error"
        assert "No recipients provided" in result["message"]

    def test_send_email_generic_error(self, controller, mock_protocol):
        """Test sending email with generic error."""

        mock_protocol.send_email.side_effect = Exception("SMTP error")

        thread_stub = SimpleNamespace(contacts=[SimpleNamespace(email="to@example.com")])

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = thread_stub

            result = controller.send_email(
                subject="Test",
                body="Body",
                thread_id=10,
            )

        assert result["status"] == "error"
        assert "Failed to send email" in result["message"]
        assert "SMTP error" in result["message"]

    def test_send_email_invalid_thread(self, controller, mock_protocol):
        """Test sending email with invalid thread id."""

        with patch("remail.controllers.email_controller.ThreadService") as thread_service:
            thread_service.return_value.get_thread_by_id.return_value = None

            result = controller.send_email(
                subject="Test",
                body="Body",
                thread_id=999,
            )

        assert result["status"] == "error"
        assert "Thread with the specified ID does not exist." in result["message"]
        mock_protocol.send_email.assert_not_called()


class TestSendEmailNewThread:
    """Tests for send_email_new_thread functionality."""

    def test_send_email_new_thread_success(self, controller, mock_protocol):
        """Test successful email send in a new thread."""

        mock_protocol.send_email.return_value = None

        conversation_data = {
            "contacts": [{"email": "to1@example.com"}, {"email": "to2@example.com"}],
        }
        thread_stub = SimpleNamespace(id=55)

        with patch("remail.controllers.email_controller.ConversationService") as conv_service:
            with patch("remail.controllers.email_controller.ThreadService") as thread_service:
                conv_service.return_value.get_conversation_by_id.return_value = conversation_data
                thread_service.return_value.create_thread.return_value = thread_stub

                result = controller.send_email_new_thread(
                    subject="Subject",
                    body="Body",
                    conversation_id=9,
                    attachments=["file.txt"],
                )

        assert result["status"] == "success"
        assert result["thread_id"] == 55
        assert result["conversation_id"] == 9

        email_arg = mock_protocol.send_email.call_args[0][0]
        assert len(email_arg.recipients) == 2
        assert email_arg.attachments[0].filename == "file.txt"

    def test_send_email_new_thread_invalid_conversation(self, controller, mock_protocol):
        """Test send_email_new_thread with invalid conversation."""

        with patch("remail.controllers.email_controller.ConversationService") as conv_service:
            conv_service.return_value.get_conversation_by_id.return_value = None

            result = controller.send_email_new_thread(
                subject="Subject",
                body="Body",
                conversation_id=999,
            )

        assert result["status"] == "error"
        assert "Invalid conversation ID" in result["message"]
        mock_protocol.send_email.assert_not_called()


class TestSendEmailNewConversation:
    """Tests for send_email_new_conversation functionality."""

    def test_send_email_new_conversation_success(self, controller, mock_protocol):
        """Test successful email send for a new conversation."""

        mock_protocol.send_email.return_value = None

        contact1 = Contact(id=1, name="User One", email_address="one@example.com")
        contact2 = Contact(id=2, name="User Two", email_address="two@example.com")
        conversation_stub = {"id": 77}
        thread_stub = SimpleNamespace(id=88)

        with patch("remail.controllers.email_controller.ContactService") as contact_service:
            with patch("remail.controllers.email_controller.ConversationService") as conv_service:
                with patch("remail.controllers.email_controller.ThreadService") as thread_service:
                    with patch("remail.controllers.email_controller.UserService") as user_service:
                        contact_service.return_value.get_contact_by_id.side_effect = [
                            contact1,
                            contact2,
                        ]
                        user_service.get_user_by_email.return_value = SimpleNamespace(id=7)
                        conv_service.return_value.create_conversation.return_value = (
                            conversation_stub
                        )
                        thread_service.return_value.create_thread.return_value = thread_stub

                        result = controller.send_email_new_conversation(
                            contact_ids=[1, 2],
                            subject="Hello",
                            body="Body",
                            attachments=["doc.pdf"],
                        )

        assert result["status"] == "success"
        assert result["thread_id"] == 88
        assert result["conversation_id"] == 77

        email_arg = mock_protocol.send_email.call_args[0][0]
        assert len(email_arg.recipients) == 2
        assert email_arg.attachments[0].filename == "doc.pdf"

    def test_send_email_new_conversation_invalid_contact(self, controller, mock_protocol):
        """Test send_email_new_conversation with a missing contact."""

        with patch("remail.controllers.email_controller.ContactService") as contact_service:
            contact_service.return_value.get_contact_by_id.return_value = None

            result = controller.send_email_new_conversation(
                contact_ids=[123],
                subject="Hello",
                body="Body",
            )

        assert result["status"] == "error"
        assert "Contact ID 123 not found" in result["message"]
        mock_protocol.send_email.assert_not_called()

    def test_send_email_new_conversation_no_recipients(self, controller, mock_protocol):
        """Test send_email_new_conversation with no recipients."""

        result = controller.send_email_new_conversation(
            contact_ids=[],
            subject="Hello",
            body="Body",
        )

        assert result["status"] == "error"
        assert "No recipients provided" in result["message"]
        mock_protocol.send_email.assert_not_called()


class TestDeleteEmail:
    """Tests for delete email functionality."""

    def test_delete_email_soft_delete(self, controller, mock_protocol):
        """Test soft delete (move to trash)."""

        mock_protocol.delete_email.return_value = None

        result = controller.delete_email(message_id="<msg123@example.com>")

        assert result["status"] == "success"
        assert "moved to trash" in result["message"]
        assert result["message_id"] == "<msg123@example.com>"
        assert result["hard_delete"] is False

        mock_protocol.delete_email.assert_called_once_with(
            message_id="<msg123@example.com>",
            hard_delete=False,
        )

    def test_delete_email_hard_delete(self, controller, mock_protocol):
        """Test hard delete (permanent)."""

        mock_protocol.delete_email.return_value = None

        result = controller.delete_email(
            message_id="<msg456@example.com>",
            hard_delete=True,
        )

        assert result["status"] == "success"
        assert "permanently deleted" in result["message"]
        assert result["message_id"] == "<msg456@example.com>"
        assert result["hard_delete"] is True

        mock_protocol.delete_email.assert_called_once_with(
            message_id="<msg456@example.com>",
            hard_delete=True,
        )

    def test_delete_email_not_logged_in(self, controller, mock_protocol):
        """Test deleting email when not logged in."""

        mock_protocol.delete_email.side_effect = ee.NotLoggedIn()

        result = controller.delete_email(message_id="<msg@example.com>")

        assert result["status"] == "error"
        assert result["message"] == "Not logged in"

    def test_delete_email_generic_error(self, controller, mock_protocol):
        """Test deleting email with generic error."""

        mock_protocol.delete_email.side_effect = Exception("Delete failed")

        result = controller.delete_email(message_id="<msg@example.com>")

        assert result["status"] == "error"
        assert "Failed to delete email" in result["message"]
        assert "Delete failed" in result["message"]


class TestEmailModelCreation:
    """Tests for internal email model creation."""

    def test_create_email_model_basic(self, controller):
        """Test creating basic email model."""

        email = controller._create_email_model(
            subject="Test",
            body="Body",
            to=["to@example.com"],
            attachments=[],
            thread_id=1,
        )

        assert email.subject == "Test"
        assert email.body == "Body"
        assert email.sender.email_address == "user@example.com"
        assert len(email.recipients) == 1
        assert email.recipients[0].kind == RecipientKind.TO
        assert email.recipients[0].contact.email_address == "to@example.com"

    def test_create_email_model_multiple_recipients(self, controller):
        """Test creating email with multiple recipients."""

        email = controller._create_email_model(
            subject="Test",
            body="Body",
            to=["to1@example.com", "to2@example.com"],
            attachments=[],
            thread_id=2,
        )

        assert len(email.recipients) == 2

        to_recipients = [r for r in email.recipients if r.kind == RecipientKind.TO]

        assert len(to_recipients) == 2


class TestEmailSerialization:
    """Tests for email serialization."""

    def test_serialize_email_with_no_recipients(self, controller):
        """Test serializing email with no recipients."""

        sender = Contact(id=1, name="Sender", email_address="sender@example.com")
        email = Email(
            id=1,
            subject="Test",
            body="Body",
            sent_at=datetime(2025, 11, 13, tzinfo=UTC),
            sender=sender,
        )
        email.recipients = []
        email.attachments = []

        result = controller._serialize_email(email)

        assert result["id"] == 1
        assert result["subject"] == "Test"
        assert result["recipients"] == []
        assert result["attachments"] == []

    def test_serialize_email_with_no_sender(self, controller):
        """Test serializing email with no sender."""

        email = Email(
            id=1,
            subject="Test",
            body="Body",
            sent_at=datetime(2025, 11, 13, tzinfo=UTC),
        )
        email.sender = None
        email.recipients = []
        email.attachments = []

        result = controller._serialize_email(email)

        assert result["sender"]["name"] is None
        assert result["sender"]["email"] is None


class TestTagEmail:
    """Tests for tag_email functionality."""

    def test_tag_email_add_success(self, controller, mock_protocol):
        """Test successfully adding a tag to an email."""

        mock_protocol.tag_email.return_value = None

        result = controller.tag_email(message_id="<test@example.com>", tag="important")

        assert result["status"] == "success"
        assert result["message"] == "Tag 'important' added to email"
        assert result["message_id"] == "<test@example.com>"
        assert result["tag"] == "important"
        assert result["action"] == "add"

        mock_protocol.tag_email.assert_called_once_with(
            message_id="<test@example.com>", tag="important", remove=False
        )

    def test_tag_email_remove_success(self, controller, mock_protocol):
        """Test successfully removing a tag from an email."""

        mock_protocol.tag_email.return_value = None

        result = controller.tag_email(message_id="<test@example.com>", tag="important", remove=True)

        assert result["status"] == "success"
        assert result["message"] == "Tag 'important' removed from email"
        assert result["message_id"] == "<test@example.com>"
        assert result["tag"] == "important"
        assert result["action"] == "remove"

        mock_protocol.tag_email.assert_called_once_with(
            message_id="<test@example.com>", tag="important", remove=True
        )

    def test_tag_email_not_logged_in(self, controller, mock_protocol):
        """Test tagging email when not logged in."""

        mock_protocol.tag_email.side_effect = ee.NotLoggedIn()

        result = controller.tag_email(message_id="<test@example.com>", tag="important")

        assert result["status"] == "error"
        assert result["message"] == "Not logged in"

    def test_tag_email_generic_error(self, controller, mock_protocol):
        """Test tagging email with generic error."""

        mock_protocol.tag_email.side_effect = Exception("IMAP error")

        result = controller.tag_email(message_id="<test@example.com>", tag="important")

        assert result["status"] == "error"
        assert result["message"] == "Failed to tag email: IMAP error"

    def test_tag_email_with_custom_tag(self, controller, mock_protocol):
        """Test adding a custom tag."""

        mock_protocol.tag_email.return_value = None

        result = controller.tag_email(message_id="<test@example.com>", tag="work")

        assert result["status"] == "success"
        assert result["tag"] == "work"

        mock_protocol.tag_email.assert_called_once_with(
            message_id="<test@example.com>", tag="work", remove=False
        )

    def test_tag_email_with_standard_flag(self, controller, mock_protocol):
        """Test adding a standard IMAP flag."""

        mock_protocol.tag_email.return_value = None

        result = controller.tag_email(message_id="<test@example.com>", tag="\\FLAGGED")

        assert result["status"] == "success"
        assert result["tag"] == "\\FLAGGED"

        mock_protocol.tag_email.assert_called_once_with(
            message_id="<test@example.com>", tag="\\FLAGGED", remove=False
        )
