from email.message import EmailMessage
from smtplib import SMTP_SSL, SMTP_SSL_PORT

from remail import errors as ee


class SmtpSender:
    """Service for sending emails via SMTP."""

    def __init__(self, host: str, username: str | None = None, password: str | None = None):
        """
        Initialize SMTP sender.

        Args:
            host: SMTP server hostname
            username: SMTP username
            password: SMTP password
        """

        self.host = host
        self.username = username
        self.password = password

    def validate_send_state(self, logged_in: bool) -> None:
        """
        Validate that we're ready to send email.

        Args:
            logged_in: Whether user is logged in

        Raises:
            NotLoggedIn: If not logged in
            InvalidLoginData: If credentials are missing
        """

        if not logged_in:
            raise ee.NotLoggedIn()

        if not self.username or not self.password:
            raise ee.InvalidLoginData()

    def send(self, msg: EmailMessage, envelope_recipients: list[str]) -> None:
        """
        Send email via SMTP.

        Args:
            msg: EmailMessage to send
            envelope_recipients: List of recipient email addresses

        Raises:
            InvalidLoginData: If credentials are not set
            Various SMTP exceptions on failure
        """

        if self.username is None or self.password is None:
            raise ee.InvalidLoginData()

        with SMTP_SSL(self.host, port=SMTP_SSL_PORT) as smtp:
            smtp.login(self.username, self.password)
            smtp.send_message(msg, from_addr=self.username, to_addrs=envelope_recipients)
