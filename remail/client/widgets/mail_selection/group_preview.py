from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ConversationDTO


class GroupPreview(ConversationPreview):
    # component representing a single contact entry
    def __init__(self, state: MainAppState, group: ConversationDTO, on_click=lambda: None):
        primary = group.custom_name if group.custom_name else group.get_member_string()
        secondary = (
            group.threads[0].last_message
            if group.threads
            else str(len(group.contacts)) + " Members"
        )

        super().__init__(
            state,
            group,
            primary,
            secondary,
            bool(group.custom_name),
            on_click,
        )
