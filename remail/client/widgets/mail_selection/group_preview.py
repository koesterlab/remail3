from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ConversationDTO


class GroupPreview(ConversationPreview):
    # component representing a single contact entry
    def __init__(self, state: MainAppState, group: ConversationDTO, on_click=lambda: None):
        primary = group.customName if group.customName else group.get_member_string()
        secondary = str(len(group.contacts)) + " Members"

        super().__init__(
            state,
            group,
            primary,
            secondary,
            bool(group.customName),
            on_click,
        )
