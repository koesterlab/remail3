import flet as ft

from remail.controllers.dtos.conversations import ConversationDTO
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
    if not getattr(contact, "is_known", True):
        initials = "?"
    elif contact.first_name and len(contact.first_name) >= 2:
        initials = (
            contact.first_name[:1]
            + (contact.last_name[:1] if contact.last_name else contact.first_name[1])
        ).upper()
    elif contact.last_name and len(contact.last_name) >= 2:
        initials = contact.last_name[:2].upper()
    else:
        initials = "@"

    # todo: use contact.is_known to switch to ft.Icon(ft.Icons.PERSON) once contact is a ContactDTO
    image = ft.Text(initials)
    image.color = ft.Colors.ON_SECONDARY
    return ft.CircleAvatar(
        content=image,
        bgcolor=ft.Colors.ON_SURFACE,
        radius=20,
        tooltip=contact.first_name
        if contact.first_name
        else "" + " " + contact.last_name
        if contact.last_name
        else "",
    )
