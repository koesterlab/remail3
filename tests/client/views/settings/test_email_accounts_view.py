"""Unit test for email_accounts_view."""

import unittest
from unittest.mock import Mock, patch

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.views.settings.email_accounts_view import create_email_accounts_view


class TestEmailAccoutsView(unittest.TestCase):
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_returns_container(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        self.assertIsInstance(result, ft.Container)
        self.assertEqual(result.padding, 20)
        self.assertEqual(result.border_radius, 10)
        self.assertEqual(result.alignment, ft.alignment.center_left)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_container_has_column(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        self.assertIsInstance(result.content, ft.Column)
        self.assertEqual(result.content.spacing, 15)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_column_has_6_titles(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        self.assertEqual(len(result.content.controls), 6)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_email_accounts_title(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        title = result.content.controls[0]

        self.assertIsInstance(title, ft.Text)
        self.assertEqual(title.value, "Email Accounts")
        self.assertEqual(title.size, 18)
        self.assertEqual(title.weight, ft.FontWeight.BOLD)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_description_text(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        description = result.content.controls[1]

        self.assertIsInstance(description, ft.Text)
        self.assertEqual(description.value, "Manage your email accounts")

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_divider(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        divider = result.content.controls[2]

        self.assertIsInstance(divider, ft.Divider)
        self.assertEqual(divider.height, 2)
        self.assertEqual(divider.color, ft.Colors.GREY_400)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_no_accounts_message(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        start_text = result.content.controls[3]

        self.assertIsInstance(start_text, ft.Text)
        self.assertEqual(start_text.value, "No accounts connected yet")

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_add_button(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]

        self.assertIsInstance(add_button, ft.Container)
        self.assertIsInstance(add_button.content, ft.OutlinedButton)
        self.assertEqual(add_button.content.text, "Add Email Account")

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_add_button_icon(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button_icon = result.content.controls[4].content

        self.assertEqual(add_button_icon.icon, ft.Icons.ADD)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_has_add_button_handler(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button_click = result.content.controls[4].content

        self.assertIsNotNone(add_button_click.on_click)
        self.assertTrue(callable(add_button_click.on_click))

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_input_panel_is_empty(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        input_panel = result.content.controls[5]

        self.assertIsInstance(input_panel, ft.Container)
        self.assertIsNone(input_panel.content)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_multiple_instances_independent(self, mock_user_service):
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state1 = AppState()
        app_state2 = AppState()

        view1 = create_email_accounts_view(page, app_state1)
        view2 = create_email_accounts_view(page, app_state2)

        self.assertIsNot(view1, view2)
        self.assertIsNot(view1.content, view2.content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
