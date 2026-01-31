import datetime
from dataclasses import dataclass

from remail.models import User
from remail.utils.session_management import session

from .contact import ContactDTO
from .thread_preview import ThreadPreviewDTO


@dataclass()
class ConversationDTO:
    id: int
    contacts: list[ContactDTO]
    threads: list[ThreadPreviewDTO]
    is_favorite: bool
    custom_name: str | None

    def __hash__(self):
        return hash(tuple(self.contacts))

    def get_member_string(self, extended: bool = False) -> str:
        def to_string(contact: ContactDTO) -> str:
            if contact.first_name and contact.last_name and len(contact.first_name) > 0:
                return (
                    (contact.first_name if extended else (contact.first_name[0] + "."))
                    + " "
                    + contact.last_name
                )
            elif contact.first_name:
                return contact.first_name
            elif contact.last_name:
                return contact.last_name
            else:
                return contact.email

        return ", ".join(to_string(c) for c in self.contacts)

    @staticmethod
    @session
    def from_model(conversation, own_mail: User) -> "ConversationDTO":
        threads = []
        for thread in conversation.threads:
            unread_count = 0
            total_count = 0
            latest_message = None
            for message in thread.messages:
                if not message.read:
                    unread_count += 1
                if not latest_message or message.sent_at > latest_message.sent_at:
                    latest_message = message
                total_count += 1
            threads.append(
                ThreadPreviewDTO(
                    thread_id=thread.id if thread.id is not None else -1,
                    title=thread.title,
                    total_count=total_count,
                    unread_count=unread_count,
                    last_message=latest_message.body if latest_message else "",
                    last_message_datetime=latest_message.sent_at
                    if latest_message
                    else datetime.datetime.min,
                )
            )

        return ConversationDTO(
            id=conversation.id if conversation.id is not None else -1,
            is_favorite=conversation.is_favorite,
            custom_name=conversation.custom_name,
            contacts=[
                ContactDTO.from_model(c)
                for c in conversation.contacts
                if c.email_address.casefold() != own_mail.email.casefold()
            ],
            threads=threads,
        )
        pass
