from email.message import EmailMessage
from unittest.mock import MagicMock, patch

import pytest

from remail import errors as ee
from remail.interfaces.email.services.smtp_sender import SmtpSender


def test_validate_send_state_ok():
    s = SmtpSender(host="smtp.example.com", username="me@example.com", password="secret")

    s.validate_send_state(logged_in=True)


def test_validate_send_state_raises_not_logged_in():
    s = SmtpSender(host="smtp.example.com", username="me@example.com", password="secret")

    with pytest.raises(ee.NotLoggedIn):
        s.validate_send_state(logged_in=False)


@pytest.mark.parametrize(
    "username,password",
    [
        (None, "secret"),
        ("me@example.com", None),
        ("", "secret"),
        ("me@example.com", ""),
        (None, None),
    ],
)
def test_validate_send_state_raises_invalid_login_data(username, password):
    s = SmtpSender(host="smtp.example.com", username=username, password=password)

    with pytest.raises(ee.InvalidLoginData):
        s.validate_send_state(logged_in=True)


def test_send_calls_smtp_correctly():
    s = SmtpSender(host="smtp.example.com", username="me@example.com", password="secret")
    msg = EmailMessage()
    msg["Subject"] = "Hi"
    recipients = ["a@x.com", "b@x.com"]

    with patch("remail.interfaces.email.services.smtp_sender.SMTP_SSL") as smtp_cls:
        smtp_conn = MagicMock()
        smtp_cls.return_value.__enter__.return_value = smtp_conn

        s.send(msg, recipients)

        smtp_cls.assert_called_once()

        args, kwargs = smtp_cls.call_args

        assert args[0] == "smtp.example.com"
        assert "port" in kwargs

        smtp_conn.login.assert_called_once_with("me@example.com", "secret")
        smtp_conn.send_message.assert_called_once_with(
            msg, from_addr="me@example.com", to_addrs=recipients
        )


def test_send_propagates_smtp_errors_on_login():
    s = SmtpSender(host="smtp.example.com", username="me@example.com", password="secret")
    msg = EmailMessage()
    recipients = ["a@x.com"]

    with patch(
        "remail.interfaces.email.services.smtp_sender.SMTP_SSL"
    ) as smtp_cls:  # <-- adjust path
        smtp_conn = MagicMock()
        smtp_cls.return_value.__enter__.return_value = smtp_conn
        smtp_conn.login.side_effect = RuntimeError("SMTP login failed")

        with pytest.raises(RuntimeError, match="SMTP login failed"):
            s.send(msg, recipients)

        smtp_conn.send_message.assert_not_called()


def test_send_propagates_smtp_errors_on_send():
    s = SmtpSender(host="smtp.example.com", username="me@example.com", password="secret")
    msg = EmailMessage()
    recipients = ["a@x.com"]

    with patch(
        "remail.interfaces.email.services.smtp_sender.SMTP_SSL"
    ) as smtp_cls:  # <-- adjust path
        smtp_conn = MagicMock()
        smtp_cls.return_value.__enter__.return_value = smtp_conn
        smtp_conn.send_message.side_effect = OSError("network down")

        with pytest.raises(IOError, match="network down"):
            s.send(msg, recipients)

        smtp_conn.login.assert_called_once()
