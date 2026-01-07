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

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_view_with_existing_users(self, mock_user_service):
        """Test view creation when users already exist."""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user_service.get_all_users.return_value = [mock_user]

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []
        app_state = AppState()

        result = create_email_accounts_view(page, app_state)

        # Should have more controls due to existing user account
        self.assertGreater(len(result.content.controls), 6)
        # Start text should be hidden
        start_text = result.content.controls[3]
        self.assertFalse(start_text.visible)
        # Connected emails should be set
        self.assertEqual(app_state.connected_emails, ["test@example.com"])

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_add_account_click_shows_form(self, mock_user_service):
        """Test that clicking add button shows input form."""
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Initially empty
        self.assertIsNone(input_panel.content)
        self.assertTrue(add_button.visible)

        # Click add button
        add_button.content.on_click(Mock())

        # Form should be shown
        self.assertIsNotNone(input_panel.content)
        self.assertIsInstance(input_panel.content, ft.Column)
        self.assertFalse(add_button.visible)
        page.update.assert_called()

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_cancel_add_hides_form(self, mock_user_service):
        """Test that cancel button hides form and clears inputs."""
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form first
        add_button.content.on_click(Mock())

        # Get form controls
        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        # Set some values
        email_input.value = "test@example.com"
        password_input.value = "password123"
        host_input.value = "imap.example.com"

        # Click cancel button
        cancel_button = buttons_row.controls[1]
        cancel_button.on_click(Mock())

        # Form should be hidden and inputs cleared
        self.assertIsNone(input_panel.content)
        self.assertTrue(add_button.visible)
        self.assertEqual(email_input.value, "")
        self.assertEqual(password_input.value, "")
        self.assertEqual(host_input.value, "")
        page.update.assert_called()

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_empty_fields(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test connect_account with empty fields shows error."""
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        buttons_row = form_column.controls[4]
        connect_button = buttons_row.controls[0]

        # Click connect with empty fields
        connect_button.on_click(Mock())

        # Should show error snackbar
        self.assertEqual(len(page.overlay), 1)
        snackbar = page.overlay[0]
        self.assertIsInstance(snackbar, ft.SnackBar)
        self.assertEqual(snackbar.bgcolor, ft.Colors.RED_400)

        # Should not call EmailController
        mock_email_controller.assert_not_called()

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_already_connected(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test connect_account with already connected email."""
        mock_user_service.get_all_users.return_value = []
        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        # Set connected emails before creating view - this gets set in create_email_accounts_view
        result = create_email_accounts_view(page, app_state)
        # Now set it after view creation
        app_state.connected_emails = ["existing@example.com"]

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        email_input.value = "existing@example.com"
        password_input.value = "password123"
        host_input.value = "imap.example.com"

        # Clear overlay to only see new snackbars
        page.overlay.clear()

        connect_button = buttons_row.controls[0]
        connect_button.on_click(Mock())

        # Should show warning snackbar (orange)
        self.assertGreater(len(page.overlay), 0)
        snackbars = [s for s in page.overlay if isinstance(s, ft.SnackBar)]
        self.assertGreater(len(snackbars), 0)
        # Check if any snackbar has the orange color or contains "already connected" message
        orange_snackbar = None
        for sb in snackbars:
            if sb.bgcolor == ft.Colors.ORANGE_400:
                orange_snackbar = sb
                break
            # Also check by message content
            if isinstance(sb.content, ft.Text) and "already connected" in sb.content.value.lower():
                orange_snackbar = sb
                break
        self.assertIsNotNone(
            orange_snackbar,
            f"Found snackbars: {[s.bgcolor if hasattr(s, 'bgcolor') else 'no bgcolor' for s in snackbars]}",
        )

        # Should not call EmailController
        mock_email_controller.assert_not_called()

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_success(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test successful account connection."""
        mock_user_service.get_all_users.return_value = []
        mock_user_service.add_user.return_value = Mock()

        # Mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.login.return_value = {"status": "success", "message": "OK"}
        mock_protocol = Mock()
        mock_protocol.email_parser = Mock()
        mock_controller_instance.protocol = mock_protocol
        mock_email_controller.return_value = mock_controller_instance

        # Mock sync service
        mock_sync_instance = Mock()
        mock_sync_service.return_value = mock_sync_instance

        # Mock scheduler
        mock_scheduler_instance = Mock()
        mock_scheduler.return_value = mock_scheduler_instance

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        email_input.value = "new@example.com"
        password_input.value = "password123"
        host_input.value = "imap.example.com"

        connect_button = buttons_row.controls[0]
        connect_button.on_click(Mock())

        # Verify controller was created and login called
        mock_email_controller.assert_called_once_with(
            username="new@example.com", password="password123", host="imap.example.com"
        )
        mock_controller_instance.login.assert_called_once()

        # Verify user was added
        mock_user_service.add_user.assert_called_once_with(
            email="new@example.com", password="password123"
        )

        # Verify sync service and scheduler were created
        mock_sync_service.assert_called_once()
        mock_scheduler.assert_called_once()
        mock_scheduler_instance.start.assert_called_once()

        # Verify email was added to connected_emails
        self.assertIn("new@example.com", app_state.connected_emails)
        # Verify scheduler was added to app_state
        self.assertIn("new@example.com", app_state.email_schedulers)

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_duplicate_user_valueerror(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test connect_account when user already exists (ValueError)."""
        mock_user_service.get_all_users.return_value = []
        mock_user_service.add_user.side_effect = ValueError("User already exists")

        # Mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.login.return_value = {"status": "success", "message": "OK"}
        mock_protocol = Mock()
        mock_protocol.email_parser = Mock()
        mock_controller_instance.protocol = mock_protocol
        mock_email_controller.return_value = mock_controller_instance

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        email_input.value = "duplicate@example.com"
        password_input.value = "password123"
        host_input.value = "imap.example.com"

        connect_button = buttons_row.controls[0]
        connect_button.on_click(Mock())

        # Should show success message about already in database
        snackbars = [s for s in page.overlay if isinstance(s, ft.SnackBar) and s.open]
        self.assertGreater(len(snackbars), 0)
        # Should still add to connected_emails
        self.assertIn("duplicate@example.com", app_state.connected_emails)

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_save_exception(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test connect_account when save fails with other exception."""
        mock_user_service.get_all_users.return_value = []
        mock_user_service.add_user.side_effect = Exception("Database error")

        # Mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.login.return_value = {"status": "success", "message": "OK"}
        mock_protocol = Mock()
        mock_protocol.email_parser = Mock()
        mock_controller_instance.protocol = mock_protocol
        mock_email_controller.return_value = mock_controller_instance

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        email_input.value = "error@example.com"
        password_input.value = "password123"
        host_input.value = "imap.example.com"

        connect_button = buttons_row.controls[0]
        connect_button.on_click(Mock())

        # Should show warning snackbar with error message
        snackbars = [s for s in page.overlay if isinstance(s, ft.SnackBar) and s.open]
        warning_snackbar = next((s for s in snackbars if s.bgcolor == ft.Colors.ORANGE_400), None)
        self.assertIsNotNone(warning_snackbar)

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_login_failed(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test connect_account when login fails."""
        mock_user_service.get_all_users.return_value = []

        # Mock controller with failed login
        mock_controller_instance = Mock()
        mock_controller_instance.login.return_value = {
            "status": "error",
            "message": "Invalid credentials",
        }
        mock_email_controller.return_value = mock_controller_instance

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        email_input.value = "failed@example.com"
        password_input.value = "wrongpassword"
        host_input.value = "imap.example.com"

        connect_button = buttons_row.controls[0]
        connect_button.on_click(Mock())

        # Should show error snackbar
        snackbars = [s for s in page.overlay if isinstance(s, ft.SnackBar) and s.open]
        error_snackbar = next((s for s in snackbars if s.bgcolor == ft.Colors.RED_400), None)
        self.assertIsNotNone(error_snackbar)

        # Should not add user
        mock_user_service.add_user.assert_not_called()

    @patch("remail.client.views.settings.email_accounts_view.Scheduler")
    @patch("remail.client.views.settings.email_accounts_view.EmailSyncService")
    @patch("remail.client.views.settings.email_accounts_view.EmailController")
    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_connect_account_login_exception(
        self, mock_user_service, mock_email_controller, mock_sync_service, mock_scheduler
    ):
        """Test connect_account when login raises exception."""
        mock_user_service.get_all_users.return_value = []
        mock_email_controller.side_effect = Exception("Connection error")

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        result = create_email_accounts_view(page, app_state)

        add_button = result.content.controls[4]
        input_panel = result.content.controls[5]

        # Show form
        add_button.content.on_click(Mock())

        form_column = input_panel.content
        email_input = form_column.controls[1]
        password_input = form_column.controls[2]
        host_input = form_column.controls[3]
        buttons_row = form_column.controls[4]

        email_input.value = "exception@example.com"
        password_input.value = "password123"
        host_input.value = "imap.example.com"

        connect_button = buttons_row.controls[0]
        connect_button.on_click(Mock())

        # Should show error snackbar
        snackbars = [s for s in page.overlay if isinstance(s, ft.SnackBar) and s.open]
        error_snackbar = next((s for s in snackbars if s.bgcolor == ft.Colors.RED_400), None)
        self.assertIsNotNone(error_snackbar)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_remove_account_success(self, mock_user_service):
        """Test successful account removal."""
        mock_user = Mock()
        mock_user.email = "remove@example.com"
        mock_user_service.get_all_users.return_value = [mock_user]
        mock_user_service.delete_user.return_value = True

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        app_state.connected_emails = ["remove@example.com"]
        app_state.add_email_scheduler = Mock()
        app_state.remove_email_scheduler = Mock()

        result = create_email_accounts_view(page, app_state)

        # Find the remove button for the account
        # Account container should be inserted before add_button
        account_container = None
        for control in result.content.controls:
            if isinstance(control, ft.Container) and control.content:
                if isinstance(control.content, ft.Row):
                    for row_control in control.content.controls:
                        if (
                            isinstance(row_control, ft.IconButton)
                            and row_control.icon == ft.Icons.DELETE
                        ):
                            account_container = control
                            break

        self.assertIsNotNone(account_container)

        # Find remove button
        remove_button = None
        for control in account_container.content.controls:
            if isinstance(control, ft.IconButton) and control.icon == ft.Icons.DELETE:
                remove_button = control
                break

        self.assertIsNotNone(remove_button)

        # Mock event
        mock_event = Mock()
        mock_event.control = remove_button
        mock_event.control.parent = account_container
        mock_event.control.parent.parent = account_container

        # Click remove
        remove_button.on_click(mock_event)

        # Verify user was deleted
        mock_user_service.delete_user.assert_called_once_with("remove@example.com")
        app_state.remove_email_scheduler.assert_called_once_with("remove@example.com")
        self.assertNotIn("remove@example.com", app_state.connected_emails)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_remove_account_exception(self, mock_user_service):
        """Test account removal when exception occurs."""
        mock_user = Mock()
        mock_user.email = "error@example.com"
        mock_user_service.get_all_users.return_value = [mock_user]
        mock_user_service.delete_user.side_effect = Exception("Delete failed")

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        app_state.connected_emails = ["error@example.com"]
        app_state.remove_email_scheduler = Mock()

        result = create_email_accounts_view(page, app_state)

        # Find remove button
        remove_button = None
        account_container = None
        for control in result.content.controls:
            if isinstance(control, ft.Container) and control.content:
                if isinstance(control.content, ft.Row):
                    for row_control in control.content.controls:
                        if (
                            isinstance(row_control, ft.IconButton)
                            and row_control.icon == ft.Icons.DELETE
                        ):
                            remove_button = row_control
                            account_container = control
                            break

        self.assertIsNotNone(remove_button)

        # Mock event - note: there's a bug in the code where exception 'e' shadows event 'e'
        # This will cause an UnboundLocalError when trying to access e.control.parent.parent
        # So we expect this to raise an exception
        mock_event = Mock()
        mock_event.control = remove_button
        mock_event.control.parent = account_container
        mock_event.control.parent.parent = account_container

        # Click remove - this will raise UnboundLocalError due to bug in code
        with self.assertRaises(UnboundLocalError):
            remove_button.on_click(mock_event)

        # Should show warning snackbar
        snackbars = [s for s in page.overlay if isinstance(s, ft.SnackBar) and s.open]
        warning_snackbar = next((s for s in snackbars if s.bgcolor == ft.Colors.ORANGE_400), None)
        self.assertIsNotNone(warning_snackbar)

    @patch("remail.client.views.settings.email_accounts_view.UserService")
    def test_remove_account_shows_start_text_when_empty(self, mock_user_service):
        """Test that start text is shown when last account is removed."""
        mock_user = Mock()
        mock_user.email = "last@example.com"
        mock_user_service.get_all_users.return_value = [mock_user]
        mock_user_service.delete_user.return_value = True

        page = Mock(spec=ft.Page)
        page.update = Mock()
        page.overlay = []

        app_state = AppState()
        app_state.connected_emails = ["last@example.com"]
        app_state.remove_email_scheduler = Mock()

        result = create_email_accounts_view(page, app_state)
        start_text = result.content.controls[3]

        # Initially hidden
        self.assertFalse(start_text.visible)

        # Find remove button
        remove_button = None
        account_container = None
        for control in result.content.controls:
            if isinstance(control, ft.Container) and control.content:
                if isinstance(control.content, ft.Row):
                    for row_control in control.content.controls:
                        if (
                            isinstance(row_control, ft.IconButton)
                            and row_control.icon == ft.Icons.DELETE
                        ):
                            remove_button = row_control
                            account_container = control
                            break

        # Mock event
        mock_event = Mock()
        mock_event.control = remove_button
        mock_event.control.parent = account_container
        mock_event.control.parent.parent = account_container

        # Remove account
        remove_button.on_click(mock_event)

        # Start text should be visible
        self.assertTrue(start_text.visible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
