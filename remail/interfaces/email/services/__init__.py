from importlib import import_module

__all__ = [
    "ContactService",
    "ConversationService",
    "EmailParser",
    "EmailSyncService",
    "FolderService",
    "MessageBuilder",
    "RecipientService",
    "SmtpSender",
    "ThreadService",
]

_LAZY_IMPORTS = {
    "ContactService": ".contact_service",
    "ConversationService": ".conversation_service",
    "EmailParser": ".email_parser",
    "EmailSyncService": ".email_sync_service",
    "FolderService": ".folder_service",
    "MessageBuilder": ".message_builder",
    "RecipientService": ".recipient_service",
    "SmtpSender": ".smtp_sender",
    "ThreadService": ".thread_service",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module = import_module(f"{__name__}{_LAZY_IMPORTS[name]}")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
