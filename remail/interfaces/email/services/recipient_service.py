"""Recipient processing service for email operations."""

from remail.enums import RecipientKind
from remail.models import Email


class RecipientService:
    """Service for processing email recipients."""

    @staticmethod
    def split_recipients(mail: Email) -> tuple[list[str], list[str], list[str]]:
        """
        Split email recipients into to, cc, and bcc lists.

        Args:
            mail: Email object with recipients

        Returns:
            Tuple of (to_list, cc_list, bcc_list)
        """

        to: list[str] = []
        cc: list[str] = []
        bcc: list[str] = []

        for r in mail.recipients:
            addr = getattr(r.contact, "email_address", None)

            if not addr:
                continue

            if r.kind is RecipientKind.TO:
                to.append(addr)

            elif r.kind is RecipientKind.CC:
                cc.append(addr)

            elif r.kind is RecipientKind.BCC:
                bcc.append(addr)

        return to, cc, bcc
