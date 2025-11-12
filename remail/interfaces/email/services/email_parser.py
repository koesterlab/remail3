from datetime import datetime
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime

from pytz import timezone

from remail.database.models import Attachment, Email
from remail.interfaces.email.utils.helpers import save_attachment

UTC = timezone("UTC")


class EmailParser:
    """Service for parsing email messages."""

    def __init__(self):
        """Initialize email parser."""
        pass

    @staticmethod
    def safe_msg_datetime(em) -> datetime | None:
        """
        Safely extract datetime from email message.

        Args:
            em: Email message object

        Returns:
            Datetime in UTC or None if extraction fails
        """

        try:
            hdr = em.get("Date")

            if hdr:
                return parsedate_to_datetime(hdr).astimezone(UTC)

        except Exception:
            pass

        return None

    @staticmethod
    def decode_header(value: str | None) -> str:
        """
        Decode email header value.

        Args:
            value: Raw header value

        Returns:
            Decoded string
        """

        if not value:
            return ""

        try:
            return str(make_header(decode_header(value)))

        except Exception:
            return value

    @staticmethod
    def extract_addresses(header_val: str | None) -> list[tuple[str, str]]:
        """
        Extract email addresses from header.

        Args:
            header_val: Header value containing addresses

        Returns:
            List of (name, address) tuples
        """

        return [(n, a) for n, a in getaddresses([header_val]) if a] if header_val else []

    def parse_email_message(self, em) -> Email:
        """
        Parse an email message into an Email object.

        Args:
            em: Raw email message object

        Returns:
            Email object
        """
        subject = self.decode_header(em.get("Subject"))
        # sender = (self.extract_addresses(em.get("From")) or [("", "")])[0][1]
        # to_list = self.extract_addresses(em.get("To"))
        # cc_list = self.extract_addresses(em.get("Cc"))
        # bcc_list = self.extract_addresses(em.get("Bcc"))

        dt = self.safe_msg_datetime(em)
        body_text: str = ""
        html_parts: list[str] = []
        attachments: list[str] = []

        if em.is_multipart():
            for part in em.walk():
                dispo = (part.get_content_disposition() or "").lower()
                ctype = (part.get_content_type() or "").lower()
                charset = part.get_content_charset() or "utf-8"

                if dispo == "attachment":
                    filename = self.decode_header(part.get_filename() or "")
                    payload = part.get_payload(decode=True)

                    if payload:
                        attachments.append(save_attachment(filename, payload, em.get("Message-Id")))

                    continue

                if ctype == "text/html":
                    payload = part.get_payload(decode=True)

                    if payload:
                        html_parts.append(payload.decode(charset, errors="replace"))

                    continue

                if ctype == "text/plain" and dispo != "attachment" and not body_text:
                    payload = part.get_payload(decode=True)

                    if payload:
                        body_text = payload.decode(charset, errors="replace")

                    continue
        else:
            charset = em.get_content_charset() or "utf-8"
            payload = em.get_payload(decode=True)

            if em.get_content_type() == "text/html":
                if payload:
                    html_parts.append(payload.decode(charset, errors="replace"))

            else:
                body_text = payload.decode(charset, errors="replace") if payload else ""

        # Create Email object with empty recipients list (contacts will be handled later)
        email = Email(
            message_id=em.get("Message-Id"),
            sender=None,  # Will be handled later with contacts
            subject=subject or "",
            body=body_text,
            recipients=[],  # Empty for now, contacts will be added later
            date=dt,
        )

        # Add attachments
        if attachments:
            email.attachments = [
                Attachment(filename=filename, email=email) for filename in attachments
            ]

        return email
