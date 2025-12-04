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

        # favorite toggle handler
        def toggle_fav():
            group.favorite = not group.favorite

        super().__init__(
            ft.Icon(ft.Icons.GROUP, color=ft.Colors.ON_SECONDARY),
            primary,
            secondary,
            group.is_favorite,
            bool(group.customName),
            toggle_fav,
            on_click,
        )
