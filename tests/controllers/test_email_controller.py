"""Tests for EmailController."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from remail import errors as ee
from remail.controllers.email_controller import EmailController
from remail.enums import RecipientKind
from remail.models import Attachment, Contact, Email, EmailReception


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


class TestFetchEmails:
    """Tests for fetch emails functionality."""

    def test_fetch_emails_success(self, controller, mock_protocol):
        """Test successful email fetching."""
        sender = Contact(id=1, name="Sender", email_address="sender@example.com")

        email1 = Email(
            id=1,
            subject="Test 1",
            body="Body 1",
            sent_at=datetime.now(UTC),
            sender=sender,
        )

        email2 = Email(
            id=2,
            subject="Test 2",
            body="Body 2",
            sent_at=datetime.now(UTC),
            sender=sender,
        )

        mock_protocol.fetch_emails.return_value = [email1, email2]

        result = controller.fetch_emails()

        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["emails"]) == 2
        assert result["emails"][0]["subject"] == "Test 1"
        assert result["emails"][1]["subject"] == "Test 2"

        mock_protocol.fetch_emails.assert_called_once_with(folder=None, since=None, flags=None)

    def test_fetch_emails_with_parameters(self, controller, mock_protocol):
        """Test fetching emails with folder and since parameters."""

        mock_protocol.fetch_emails.return_value = []
        since_date = datetime(2025, 1, 1, tzinfo=UTC)

        result = controller.fetch_emails(
            folder="INBOX",
            since=since_date,
            flags=["UNSEEN"],
        )

        assert result["status"] == "success"
        assert result["count"] == 0

        mock_protocol.fetch_emails.assert_called_once_with(
            folder="INBOX",
            since=since_date,
            flags=["UNSEEN"],
        )

    def test_fetch_emails_not_logged_in(self, controller, mock_protocol):
        """Test fetching emails when not logged in."""

        mock_protocol.fetch_emails.side_effect = ee.NotLoggedIn()
        result = controller.fetch_emails()

        assert result["status"] == "error"
        assert result["message"] == "Not logged in"
        assert result["count"] == 0
        assert result["emails"] == []

    def test_fetch_emails_generic_error(self, controller, mock_protocol):
        """Test fetching emails with generic error."""

        mock_protocol.fetch_emails.side_effect = Exception("Network error")

        result = controller.fetch_emails()

        assert result["status"] == "error"
        assert "Failed to fetch emails" in result["message"]
        assert "Network error" in result["message"]
        assert result["count"] == 0
        assert result["emails"] == []

    def test_fetch_emails_serialization(self, controller, mock_protocol):
        """Test email serialization includes all fields."""

        sender = Contact(id=1, name="John Doe", email_address="john@example.com")
        recipient_contact = Contact(id=2, name="Jane Doe", email_address="jane@example.com")

        email = Email(
            id=10,
            subject="Hello",
            body="World",
            sent_at=datetime(2025, 11, 13, 10, 30, 0, tzinfo=UTC),
            sender=sender,
        )

        email.recipients = [
            EmailReception(
                kind=RecipientKind.TO,
                email=email,
                contact=recipient_contact,
            )
        ]

        email.attachments = [Attachment(id=1, filename="file.txt", email=email)]

        mock_protocol.fetch_emails.return_value = [email]

        result = controller.fetch_emails()

        assert result["status"] == "success"
        assert result["count"] == 1

        serialized = result["emails"][0]

        assert serialized["id"] == 10
        assert serialized["subject"] == "Hello"
        assert serialized["body"] == "World"
        assert serialized["sent_at"] == "2025-11-13T10:30:00+00:00"
        assert serialized["sender"]["name"] == "John Doe"
        assert serialized["sender"]["email"] == "john@example.com"
        assert len(serialized["recipients"]) == 1
        assert serialized["recipients"][0]["kind"] == "to"
        assert serialized["recipients"][0]["email"] == "jane@example.com"
        assert len(serialized["attachments"]) == 1
        assert serialized["attachments"][0] == "file.txt"


class TestSendEmail:
    """Tests for send email functionality."""

    def test_send_email_success(self, controller, mock_protocol):
        """Test successful email sending."""

        mock_protocol.send_email.return_value = None

        result = controller.send_email(
            subject="Test Subject",
            body="Test Body",
            to=["recipient@example.com"],
        )

        assert result["status"] == "success"
        assert result["message"] == "Email sent successfully"
        assert "email" in result

        mock_protocol.send_email.assert_called_once()

    def test_send_email_with_all_recipients(self, controller, mock_protocol):
        """Test sending email with TO, CC, and BCC recipients."""

        mock_protocol.send_email.return_value = None

        result = controller.send_email(
            subject="Test",
            body="Body",
            to=["to@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
        )

        assert result["status"] == "success"

        call_args = mock_protocol.send_email.call_args
        email_arg = call_args[0][0]

        assert email_arg.subject == "Test"
        assert email_arg.body == "Body"
        assert len(email_arg.recipients) == 3

        kinds = {rec.kind for rec in email_arg.recipients}
        assert RecipientKind.TO in kinds
        assert RecipientKind.CC in kinds
        assert RecipientKind.BCC in kinds

    def test_send_email_with_attachments(self, controller, mock_protocol):
        """Test sending email with attachments."""

        mock_protocol.send_email.return_value = None

        result = controller.send_email(
            subject="Test",
            body="Body",
            to=["to@example.com"],
            attachments=["file1.pdf", "file2.jpg"],
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

        result = controller.send_email(
            subject="Test",
            body="Body",
            to=["to@example.com"],
        )

        assert result["status"] == "error"
        assert result["message"] == "Not logged in"

    def test_send_email_no_recipients(self, controller, mock_protocol):
        """Test sending email with no recipients raises ValueError."""

        mock_protocol.send_email.side_effect = ValueError("No recipients provided.")

        result = controller.send_email(
            subject="Test",
            body="Body",
        )

        assert result["status"] == "error"
        assert "No recipients provided" in result["message"]

    def test_send_email_generic_error(self, controller, mock_protocol):
        """Test sending email with generic error."""

        mock_protocol.send_email.side_effect = Exception("SMTP error")

        result = controller.send_email(
            subject="Test",
            body="Body",
            to=["to@example.com"],
        )

        assert result["status"] == "error"
        assert "Failed to send email" in result["message"]
        assert "SMTP error" in result["message"]


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
            cc=[],
            bcc=[],
            attachments=[],
        )

        assert email.subject == "Test"
        assert email.body == "Body"
        assert email.sender.email_address == "user@example.com"
        assert len(email.recipients) == 1
        assert email.recipients[0].kind == RecipientKind.TO
        assert email.recipients[0].contact.email_address == "to@example.com"

    def test_create_email_model_multiple_recipients(self, controller):
        """Test creating email with multiple recipient types."""

        email = controller._create_email_model(
            subject="Test",
            body="Body",
            to=["to1@example.com", "to2@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            attachments=[],
        )

        assert len(email.recipients) == 4

        to_recipients = [r for r in email.recipients if r.kind == RecipientKind.TO]
        cc_recipients = [r for r in email.recipients if r.kind == RecipientKind.CC]
        bcc_recipients = [r for r in email.recipients if r.kind == RecipientKind.BCC]

        assert len(to_recipients) == 2
        assert len(cc_recipients) == 1
        assert len(bcc_recipients) == 1


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
