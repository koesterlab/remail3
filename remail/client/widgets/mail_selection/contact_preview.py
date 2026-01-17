from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ConversationDTO


class ContactPreview(ConversationPreview):
    # component representing a single contact entry
    def __init__(self, state: MainAppState, conversation: ConversationDTO, on_click=lambda: None):
        contact = conversation.contacts[0]
        full_name = f"{contact.first_name} {contact.last_name}".strip()

        # favorite toggle handler
        def toggle_fav():
            conversation.is_favorite = not conversation.is_favorite

        super().__init__(
            state,
            conversation,
            full_name if contact.is_known else contact.email,
            full_name if not contact.is_known else contact.email,
            contact.is_known,
            on_click,
        )
