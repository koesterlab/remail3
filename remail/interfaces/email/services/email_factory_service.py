"""Service for creating Email objects from raw email data."""

from datetime import datetime
from typing import TYPE_CHECKING

from remail.enums import RecipientKind
from remail.models import Attachment, Email, EmailReception

if TYPE_CHECKING:
    from remail.controller import EmailController  # type: ignore[import-not-found]


class EmailFactory:
    """Service for creating Email objects from raw email data."""

    @staticmethod
    def create_email(
        uid: str,
        sender: str,
        subject: str,
        body: str,
        attachments: list[str],
        to_recipients: list[tuple[str, str]],
        cc_recipients: list[tuple[str, str]],
        bcc_recipients: list[tuple[str, str]],
        date: datetime,
        controller: "EmailController",
    ) -> Email:
        """
        Create an Email object from raw email data.

        Args:
            uid: Unique message ID
            sender: Sender email address
            subject: Email subject
            body: Email body text
            attachments: List of attachment file paths
            to_recipients: List of (name, email) tuples for TO recipients
            cc_recipients: List of (name, email) tuples for CC recipients
            bcc_recipients: List of (name, email) tuples for BCC recipients
            date: Email datetime
            controller: EmailController instance for contact management
            html_files: Optional list of HTML content

        Returns:
            Populated Email object
        """

        sender_contact = controller.get_contact(sender)
        recipients = [
            EmailReception(
                contact=controller.get_contact(recipient[1], recipient[0]),
                kind=RecipientKind.TO,
            )
            for recipient in to_recipients
        ]

        if cc_recipients:
            recipients += [
                EmailReception(
                    contact=controller.get_contact(recipient[1], recipient[0]),
                    kind=RecipientKind.CC,
                )
                for recipient in cc_recipients
            ]

        if bcc_recipients:
            recipients += [
                EmailReception(
                    contact=controller.get_contact(recipient[1], recipient[0]),
                    kind=RecipientKind.BCC,
                )
                for recipient in bcc_recipients
            ]

        email = Email(
            message_id=uid,
            sender=sender_contact,
            subject=subject,
            body=body,
            recipients=recipients,
            date=date,
        )

        attachments_class = [Attachment(filename=filename, email=email) for filename in attachments]
        email.attachments = attachments_class

        return email
