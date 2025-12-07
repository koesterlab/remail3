import flet as ft
from remail.controllers.dtos.conversations import ConversationDTO


def create_profile_picture(conversation: ConversationDTO):
    #todo: custom profile pictures
    if len(conversation.contacts) == 1:
        contact = conversation.contacts[0]

        initials = (
                contact.first_name[:1] + (contact.last_name[:1] if contact.last_name else "")
        ).upper()

        image = ft.Text(initials) if contact.is_known else ft.Icon(ft.Icons.PERSON)
    else:
        image = ft.Icon(ft.Icons.GROUP, color=ft.Colors.ON_SECONDARY)

    image.color = ft.Colors.ON_SECONDARY
    return ft.CircleAvatar(content=image, bgcolor=ft.Colors.ON_SURFACE, radius=20)