"""Utility functions for email operations."""

from datetime import datetime
from typing import TYPE_CHECKING

from remail.database.models import Attachment, Email, EmailReception, RecipientKind

if TYPE_CHECKING:
    from remail.controller import EmailController  # type: ignore[import-not-found]


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
    html_files: list[str] | None = None,
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
            kind=RecipientKind.to,
        )
        for recipient in to_recipients
    ]
    if cc_recipients:
        recipients += [
            EmailReception(
                contact=controller.get_contact(recipient[1], recipient[0]),
                kind=RecipientKind.cc,
            )
            for recipient in cc_recipients
        ]
    if bcc_recipients:
        recipients += [
            EmailReception(
                contact=controller.get_contact(recipient[1], recipient[0]),
                kind=RecipientKind.bcc,
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


def parse_permission_string(perm_str: str) -> int:
    """
    Convert a permission string (e.g., 'rwxrw-r--') to octal integer.

    Args:
        perm_str: Permission string in rwx format (9 characters)

    Returns:
        Octal permission value

    Raises:
        ValueError: If string is not 9 characters
    """
    if len(perm_str) != 9:
        raise ValueError(f"Permission string must be 9 characters, got {len(perm_str)}")

    val = 0
    for group_idx in range(3):  # owner, group, others
        for perm_idx in range(3):  # read, write, execute
            char_idx = group_idx * 3 + perm_idx
            if perm_str[char_idx] != "-":
                val += (8 ** (2 - group_idx)) * (2 ** (2 - perm_idx))

    return val
