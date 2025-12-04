import flet as ft

from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ConversationDTO


class ContactPreview(ConversationPreview):
    # component representing a single contact entry
    def __init__(self, conversation: ConversationDTO, on_click=lambda: None):
        contact = conversation.contacts[0]

        initials = (
            contact.first_name[:1] + (contact.last_name[:1] if contact.last_name else "")
        ).upper()
        full_name = f"{contact.first_name} {contact.last_name}".strip()

        # favorite toggle handler
        def toggle_fav():
            conversation.is_favorite = not conversation.is_favorite

        super().__init__(
            ft.Text(initials) if contact.is_known else ft.Icon(ft.Icons.PERSON),
            full_name if contact.is_known else contact.email,
            full_name if not contact.is_known else contact.email,
            conversation.is_favorite,
            contact.is_known,
            toggle_fav,
            on_click,
        )
