import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime

from werkzeug.utils import secure_filename

from remail.models import Email

from .attachment import AttachmentDTO
from .sender import SenderDTO


@dataclass
class MessageContentDTO:
    body: str
    attachments: list[AttachmentDTO]


@dataclass
class MessageDTO:
    id: int
    sender: SenderDTO
    subject: str
    content: MessageContentDTO
    sent_at: datetime

    @staticmethod
    def _attachment_path(mail: Email, filename: str) -> str:
        message_id = secure_filename(mail.message_id or "").replace(".", "_")
        name, ext = os.path.splitext(filename)
        safe_name = secure_filename((name.replace(".", "")[:50] + ext).strip())
        path = os.path.abspath(os.path.join("remail", "database", "attachments", message_id, safe_name))
        return path if os.path.exists(path) else ""

    @staticmethod
    def from_model(mail: Email):
        return MessageDTO(
            id=mail.id if mail.id else -1,
            sender=SenderDTO(
                id=mail.sender.id,
                first_name=mail.sender.first_name if mail.sender.first_name else "",
                last_name=mail.sender.last_name
                if mail.sender.last_name
                else mail.sender.name
                if mail.sender.name
                else "",
                email=mail.sender.email_address,
            ),
            subject=mail.thread.title,
            content=MessageContentDTO(
                body=mail.body,
                attachments=[
                    AttachmentDTO(
                        file_name=att.filename,
                        file_size=os.path.getsize(path)
                        if (path := MessageDTO._attachment_path(mail, att.filename))
                        else 0,
                        file_type=mimetypes.guess_type(att.filename)[0]
                        or "application/octet-stream",
                        url=path,
                    )
                    for att in mail.attachments
                ],
            ),
            sent_at=mail.sent_at,
        )
