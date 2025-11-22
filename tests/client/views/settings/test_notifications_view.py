"""Unit tests for notifications_view."""

from unittest.mock import Mock

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.views.settings.notifications_view import create_notifications_view


class TestCreateNotificationsView:
    """Test suite for create_notifications_view function."""

    def test_returns_container(self):
        """Test that create_notifications_view returns a Container."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        assert isinstance(result, ft.Container)

    def test_container_has_column(self):
        """Test that Container content is a Column."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        assert isinstance(result.content, ft.Column)

    def test_has_notifications_title(self):
        """Test that view has 'Notifications' title."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        title = result.content.controls[0]

        assert isinstance(title, ft.Text)
        assert title.value == "Notifications"
        assert title.size == 18
        assert title.weight == ft.FontWeight.BOLD

    def test_has_description_text(self):
        """Test that view has description text."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        description = result.content.controls[1]

        assert isinstance(description, ft.Text)
        assert description.value == "Customize how and when you receive notifications"

    def test_has_divider(self):
        """Test that view has a divider."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        divider = result.content.controls[2]

        assert isinstance(divider, ft.Divider)
        assert divider.height == 2
        assert divider.color == ft.Colors.BLACK

    def test_has_desktop_notifications_row(self):
        """Test that view has desktop notifications row."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[3]

        assert isinstance(row, ft.Row)
        assert len(row.controls) == 2

    def test_desktop_notifications_has_label(self):
        """Test that desktop notifications row has correct label."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[3]
        label = row.controls[0]

        assert isinstance(label, ft.Text)
        assert label.value == "Get notified on your desktop"
        assert label.expand is True

    def test_desktop_notifications_has_switch(self):
        """Test that desktop notifications row has a switch."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[3]
        switch = row.controls[1]

        assert isinstance(switch, ft.Switch)

    def test_desktop_notifications_switch_default_value(self):
        """Test that desktop notifications switch has default value from app_state."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(desktop_notifications=True)

        result = create_notifications_view(page, app_state)
        row = result.content.controls[3]
        switch = row.controls[1]

        assert switch.value is True

    def test_desktop_notifications_switch_false_value(self):
        """Test that desktop notifications switch can be False."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(desktop_notifications=False)

        result = create_notifications_view(page, app_state)
        row = result.content.controls[3]
        switch = row.controls[1]

        assert switch.value is False

    def test_desktop_notifications_switch_has_handler(self):
        """Test that desktop notifications switch has an on_change handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[3]
        switch = row.controls[1]

        assert switch.on_change is not None
        assert callable(switch.on_change)

    def test_has_email_notifications_row(self):
        """Test that view has email notifications row."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[4]

        assert isinstance(row, ft.Row)
        assert len(row.controls) == 2

    def test_email_notifications_has_label(self):
        """Test that email notifications row has correct label."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[4]
        label = row.controls[0]

        assert isinstance(label, ft.Text)
        assert label.value == "Get notified about new emails"
        assert label.expand is True

    def test_email_notifications_has_switch(self):
        """Test that email notifications row has a switch."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[4]
        switch = row.controls[1]

        assert isinstance(switch, ft.Switch)

    def test_email_notifications_switch_default_value(self):
        """Test that email notifications switch has default value from app_state."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(email_notifications=True)

        result = create_notifications_view(page, app_state)
        row = result.content.controls[4]
        switch = row.controls[1]

        assert switch.value is True

    def test_email_notifications_switch_false_value(self):
        """Test that email notifications switch can be False."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(email_notifications=False)

        result = create_notifications_view(page, app_state)
        row = result.content.controls[4]
        switch = row.controls[1]

        assert switch.value is False

    def test_email_notifications_switch_has_handler(self):
        """Test that email notifications switch has an on_change handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[4]
        switch = row.controls[1]

        assert switch.on_change is not None
        assert callable(switch.on_change)

    def test_has_quiet_hours_row(self):
        """Test that view has quiet hours row."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[5]

        assert isinstance(row, ft.Row)
        assert len(row.controls) == 2

    def test_quiet_hours_has_label(self):
        """Test that quiet hours row has correct label."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[5]
        label = row.controls[0]

        assert isinstance(label, ft.Text)
        assert label.value == "No notifications between 10 PM and 8 AM"
        assert label.expand is True

    def test_quiet_hours_has_switch(self):
        """Test that quiet hours row has a switch."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[5]
        switch = row.controls[1]

        assert isinstance(switch, ft.Switch)

    def test_quiet_hours_switch_default_value(self):
        """Test that quiet hours switch has default value from app_state."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(quiet_hours=False)

        result = create_notifications_view(page, app_state)
        row = result.content.controls[5]
        switch = row.controls[1]

        assert switch.value is False

    def test_quiet_hours_switch_true_value(self):
        """Test that quiet hours switch can be True."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState(quiet_hours=True)

        result = create_notifications_view(page, app_state)
        row = result.content.controls[5]
        switch = row.controls[1]

        assert switch.value is True

    def test_quiet_hours_switch_has_handler(self):
        """Test that quiet hours switch has an on_change handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        row = result.content.controls[5]
        switch = row.controls[1]

        assert switch.on_change is not None
        assert callable(switch.on_change)

    def test_has_apply_button(self):
        """Test that view has an Apply button."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        button_container = result.content.controls[6]

        assert isinstance(button_container, ft.Container)
        assert isinstance(button_container.content, ft.OutlinedButton)
        assert button_container.content.text == "Apply"

    def test_apply_button_has_handler(self):
        """Test that Apply button has an on_click handler."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        button_container = result.content.controls[6]
        button = button_container.content

        assert button.on_click is not None
        assert callable(button.on_click)

    def test_apply_button_centered(self):
        """Test that Apply button container is centered."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)
        button_container = result.content.controls[6]

        assert button_container.alignment == ft.alignment.center

    def test_column_spacing(self):
        """Test that Column has correct spacing."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        assert result.content.spacing == 15

    def test_container_padding(self):
        """Test that Container has correct padding."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        assert result.padding == 20

    def test_container_border_radius(self):
        """Test that Container has correct border radius."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        assert result.border_radius == 10

    def test_container_alignment(self):
        """Test that Container has correct alignment."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        assert result.alignment == ft.alignment.center_left

    def test_all_controls_present(self):
        """Test that view has all 7 expected controls."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        # Title, description, divider, 3 notification rows, apply button
        assert len(result.content.controls) == 7

    def test_multiple_instances_independent(self):
        """Test that multiple view instances are independent."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state1 = AppState(
            desktop_notifications=True, email_notifications=True, quiet_hours=False
        )
        app_state2 = AppState(
            desktop_notifications=False, email_notifications=False, quiet_hours=True
        )

        view1 = create_notifications_view(page, app_state1)
        view2 = create_notifications_view(page, app_state2)

        # Check desktop notifications switches have different values
        desktop_switch1 = view1.content.controls[3].controls[1]
        desktop_switch2 = view2.content.controls[3].controls[1]

        assert desktop_switch1.value is True
        assert desktop_switch2.value is False

        # Check email notifications switches have different values
        email_switch1 = view1.content.controls[4].controls[1]
        email_switch2 = view2.content.controls[4].controls[1]

        assert email_switch1.value is True
        assert email_switch2.value is False

        # Check quiet hours switches have different values
        quiet_switch1 = view1.content.controls[5].controls[1]
        quiet_switch2 = view2.content.controls[5].controls[1]

        assert quiet_switch1.value is False
        assert quiet_switch2.value is True

    def test_all_notifications_enabled_by_default(self):
        """Test that desktop and email notifications are enabled by default."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        desktop_switch = result.content.controls[3].controls[1]
        email_switch = result.content.controls[4].controls[1]

        assert desktop_switch.value is True
        assert email_switch.value is True

    def test_quiet_hours_disabled_by_default(self):
        """Test that quiet hours is disabled by default."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        app_state = AppState()

        result = create_notifications_view(page, app_state)

        quiet_switch = result.content.controls[5].controls[1]

        assert quiet_switch.value is False
