# test_conversation_preview.py
import unittest

import flet as ft

from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO
from remail.enums import ContactType


class TestConversationPreview(unittest.TestCase):
    def setUp(self):
        # Dummy Kontakt
        self.contact = ContactDTO(
            id=1,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.conversation = ConversationDTO(
            contacts=[self.contact], threads=[], is_favorite=True, customName=None
        )

    def test_registered_contact_preview(self):
        fav_called = {"called": False}
        click_called = {"called": False}

        def on_toggle_fav():
            fav_called["called"] = True

        def on_click():
            click_called["called"] = True

        preview = ConversationPreview(
            self.conversation,
            primary_text="Max Mustermann",
            secondary_text="max@example.com",
            registered=True,
            on_click=on_click,
        )

        # Prüfen von Avatar und Column
        row = preview.content
        avatar = row.controls[0]
        self.assertIsInstance(avatar, ft.CircleAvatar)
        self.assertEqual(avatar.content.value, "MM")
        col = row.controls[1]
        self.assertIsInstance(col, ft.Column)
        primary_row = col.controls[0]
        secondary_row = col.controls[1]
        self.assertEqual(primary_row.controls[0].value, "Max Mustermann")
        self.assertEqual(secondary_row.controls[0].value, "max@example.com")

        # Favoriten-Button prüfen
        icon_btn_row = row.controls[2]
        fav_button = icon_btn_row.controls[0]
        self.assertEqual(fav_button.icon, ft.Icons.STAR)
        self.assertTrue(fav_button.visible)
        # Toggle Favorit aufrufen
        fav_button.on_click(None)
        self.assertFalse(self.conversation.is_favorite)

        # on_click auf Container aufrufen
        preview.on_click(None)
        self.assertTrue(click_called["called"])

        # on_hover sichtbarkeitsänderung testen
        fav_button.visible = False
        # preview.on_hover(Mock(data="true"))   #doesnt work with mocked component
        # self.assertTrue(fav_button.visible)

    def test_unregistered_contact_preview(self):
        preview = ConversationPreview(
            self.conversation,
            primary_text="Unknown",
            secondary_text="unknown@example.com",
            registered=False,
            on_click=lambda: None,
        )

        icon_btn_row = preview.content.controls[2]
        self.assertEqual(len(icon_btn_row.controls), 2)
        self.assertEqual(icon_btn_row.controls[0].icon, ft.Icons.ADD)
        self.assertEqual(icon_btn_row.controls[1].icon, ft.Icons.DELETE)


if __name__ == "__main__":
    unittest.main()
