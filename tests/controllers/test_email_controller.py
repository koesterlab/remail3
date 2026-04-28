"""Tests for EmailController."""

from unittest.mock import MagicMock, patch

from remail.controllers.email_controller import EmailController
from remail.enums import AuthMethods, ConnectionSecurity


class TestCheckCredentials:
    """Tests for EmailController.check_credentials."""

    def test_check_credentials_returns_protocol_when_connection_succeeds(self):
        """It should return the created protocol when connection test passes."""
        controller = EmailController()

        with patch("remail.controllers.email_controller.ImapProtocol") as mock_protocol_cls:
            protocol_instance = MagicMock()
            protocol_instance.test_connection.return_value = True
            mock_protocol_cls.return_value = protocol_instance

            result = controller.check_credentials(
                imap_username="imap_user@example.com",
                imap_host="imap.example.com",
                imap_port=993,
                imap_password="password",
                imap_security=ConnectionSecurity.SSL_TLS,
                imap_method=AuthMethods.PASSWORD,
                smtp_username="smtp_user@example.com",
                smtp_host="smtp.example.com",
                smtp_port=465,
                smtp_password="password",
                smtp_security=ConnectionSecurity.SSL_TLS,
                smtp_method=AuthMethods.PASSWORD,
            )

        assert result is protocol_instance
        mock_protocol_cls.assert_called_once_with(
            imap_username="imap_user@example.com",
            imap_host="imap.example.com",
            imap_port=993,
            imap_password="password",
            imap_method=AuthMethods.PASSWORD,
            imap_security=ConnectionSecurity.SSL_TLS,
            smtp_username="smtp_user@example.com",
            smtp_host="smtp.example.com",
            smtp_port=465,
            smtp_password="password",
            smtp_method=AuthMethods.PASSWORD,
            smtp_security=ConnectionSecurity.SSL_TLS,
        )
        protocol_instance.test_connection.assert_called_once()

    def test_check_credentials_returns_none_when_connection_fails(self):
        """It should return None when connection test returns False."""
        controller = EmailController()

        with patch("remail.controllers.email_controller.ImapProtocol") as mock_protocol_cls:
            protocol_instance = MagicMock()
            protocol_instance.test_connection.return_value = False
            mock_protocol_cls.return_value = protocol_instance

            result = controller.check_credentials(
                imap_username="imap_user@example.com",
                imap_host="imap.example.com",
                imap_port=993,
                imap_password="password",
                imap_security=ConnectionSecurity.SSL_TLS,
                imap_method=AuthMethods.PASSWORD,
                smtp_username="smtp_user@example.com",
                smtp_host="smtp.example.com",
                smtp_port=465,
                smtp_password="password",
                smtp_security=ConnectionSecurity.SSL_TLS,
                smtp_method=AuthMethods.PASSWORD,
            )

        assert result is None
        protocol_instance.test_connection.assert_called_once()

    def test_check_credentials_returns_none_when_connection_raises(self):
        """It should return None when connection test raises an exception."""
        controller = EmailController()

        with patch("remail.controllers.email_controller.ImapProtocol") as mock_protocol_cls:
            protocol_instance = MagicMock()
            protocol_instance.test_connection.side_effect = Exception("connection error")
            mock_protocol_cls.return_value = protocol_instance

            result = controller.check_credentials(
                imap_username="imap_user@example.com",
                imap_host="imap.example.com",
                imap_port=993,
                imap_password="password",
                imap_security=ConnectionSecurity.SSL_TLS,
                imap_method=AuthMethods.PASSWORD,
                smtp_username="smtp_user@example.com",
                smtp_host="smtp.example.com",
                smtp_port=465,
                smtp_password="password",
                smtp_security=ConnectionSecurity.SSL_TLS,
                smtp_method=AuthMethods.PASSWORD,
            )

        assert result is None
        protocol_instance.test_connection.assert_called_once()
