from dataclasses import dataclass, field

from remail.controllers.dtos.conversations import ContactDTO, ThreadPreviewDTO


@dataclass
class MessageDTO:
    id: int
    sender: ContactDTO
    subject: str
    content: str
    sent_at: str  # ISO timestamp
    attachments: list[str] = field(default_factory=list)


@dataclass
class ThreadDTO(ThreadPreviewDTO):
    messages: list[MessageDTO]
