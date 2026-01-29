from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ConversationDTO


class ContactPreview(ConversationPreview):
    # component representing a single contact entry
    def __init__(self, state: MainAppState, conversation: ConversationDTO, on_click=lambda: None):
        contact = conversation.contacts[0] if conversation.contacts else None
        full_name = ""
        if contact:
            full_name = f"{contact.first_name} {contact.last_name}".strip()
            if not full_name:
                full_name = contact.email
        else:
            full_name = conversation.custom_name or "Unknown contact"
        last_message = (
            conversation.threads[0].last_message if conversation.threads else "No messages yet"
        )

        # favorite toggle handler
        def toggle_fav():
            conversation.is_favorite = not conversation.is_favorite

        super().__init__(
            state,
            conversation,
            full_name,
            last_message,
            contact.is_known if contact else False,
            on_click,
        )
