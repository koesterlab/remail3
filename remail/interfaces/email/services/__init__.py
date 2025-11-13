"""Email service modules for IMAP protocol."""

from .email_parser import EmailParser
from .folder_service import FolderService
from .message_builder import MessageBuilder
from .recipient_service import RecipientService
from .smtp_sender import SmtpSender
from .tag_service import TagService

__all__ = [
    "EmailParser",
    "FolderService",
    "MessageBuilder",
    "RecipientService",
    "SmtpSender",
    "TagService",
]
