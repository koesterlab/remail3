import flet as ft

from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ConversationDTO


class GroupPreview(ConversationPreview):
    # component representing a single contact entry
    def __init__(self, group: ConversationDTO, on_click=lambda: None):
        primary = (
            group.customName
            if group.customName
            else ", ".join(
                contact.first_name[0] + ". " + contact.last_name for contact in group.contacts
            )
        )
        secondary = str(len(group.contacts)) + " Members"

        super().__init__(
            group,
            primary,
            secondary,
            bool(group.customName),
            on_click,
        )
