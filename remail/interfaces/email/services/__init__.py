"""Email service modules for IMAP protocol."""

from .contact_service import ContactService
from .conversation_service import ConversationService
from .email_parser import EmailParser
from .email_sync_service import EmailSyncService
from .folder_service import FolderService
from .message_builder import MessageBuilder
from .recipient_service import RecipientService
from .smtp_sender import SmtpSender
from .tag_service import TagService
from .thread_service import ThreadService

__all__ = [
    "ContactService",
    "ConversationService",
    "EmailParser",
    "EmailSyncService",
    "FolderService",
    "MessageBuilder",
    "RecipientService",
    "SmtpSender",
    "TagService",
    "ThreadService",
]
