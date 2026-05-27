import mimetypes
import os
from collections.abc import Iterable
from email.message import EmailMessage


class MessageBuilder:
    """Service for building and composing email messages."""

    @staticmethod
    def build_message(
        *,
        subject: str,
        body: str,
        from_addr: str,
        to: Iterable[str],
        cc: Iterable[str],
    ) -> EmailMessage:
        """
        Build an email message.

        Args:
            subject: Email subject line
            body: Email body text
            from_addr: Sender email address
            to: List of primary recipients
            cc: List of CC recipients

        Returns:
            EmailMessage object ready to send
        """
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr

        if to:
            msg["To"] = ", ".join(to)

        if cc:
            msg["Cc"] = ", ".join(cc)

        msg.set_content(body)

        return msg

    @staticmethod
    def attach_files(msg: EmailMessage, paths: Iterable[str]) -> None:
        """
        Attach files to an email message.

        Args:
            msg: EmailMessage to attach files to
            paths: Iterable of file paths to attach

        Raises:
            FileNotFoundError: If any attachment path doesn't exist
        """

        for p in paths:
            path = os.path.abspath(p)

            if not (os.path.exists(path) and os.path.isfile(path)):
                raise FileNotFoundError(f"Attachment not found: {p}")

            maintype, subtype = MessageBuilder._guess_mime(path)

            with open(path, "rb") as f:
                data = f.read()

            msg.add_attachment(
                data, maintype=maintype, subtype=subtype, filename=os.path.basename(path)
            )

    @staticmethod
    def _guess_mime(path: str) -> tuple[str, str]:
        """
        Guess MIME type for a file.

        Args:
            path: File path

        Returns:
            Tuple of (main_type, sub_type)
        """

        mime, _ = mimetypes.guess_type(path)

        if not mime:
            return "application", "octet-stream"

        main, sub = mime.split("/", 1)

        return main or "application", sub or "octet-stream"
