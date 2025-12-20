import flet as ft

from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO
from remail.controllers.dtos.threads import SenderDTO


def create_profile_picture(conversation: ConversationDTO):
    # todo: custom profile pictures
    if len(conversation.contacts) == 1:
        contact = conversation.contacts[0]
        return create_contact_picture(contact)

    else:
        image = ft.Icon(ft.Icons.GROUP, color=ft.Colors.ON_SECONDARY)
        image.color = ft.Colors.ON_SECONDARY
        return ft.CircleAvatar(content=image, bgcolor=ft.Colors.ON_SURFACE, radius=20)


def create_contact_picture(contact: SenderDTO):
    initials = (
        contact.first_name[:1] + (contact.last_name[:1] if contact.last_name else "")
    ).upper()
    image = ft.Text(initials) if True else ft.Icon(ft.Icons.PERSON) #todo contact.is_known make contact ContactDTO
    image.color = ft.Colors.ON_SECONDARY
    return ft.CircleAvatar(
        content=image,
        bgcolor=ft.Colors.ON_SURFACE,
        radius=20,
        tooltip=contact.first_name + " " + contact.last_name,
    )
