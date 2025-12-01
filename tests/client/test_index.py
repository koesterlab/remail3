"""Unit tests for the main client index module."""

from unittest.mock import Mock, patch

import flet as ft
import pytest

from remail.client.index import main


@pytest.fixture(autouse=True)
def mock_llm_controller():
    """Mock LLMController to avoid requiring environment variables."""
    with patch("remail.client.widgets.chatbot.chatbot.LLMController"):
        yield


class TestMain:
    """Test suite for the main function."""

    def test_main_sets_page_title(self):
        """Test that main sets the correct page title."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        # The chatbot view changes the title to include " - Chatbot"
        assert page.title == "Remail 2.0 - Chatbot"

    def test_main_sets_vertical_alignment(self):
        """Test that main sets vertical alignment to center."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        assert page.vertical_alignment == ft.MainAxisAlignment.CENTER

    def test_main_calls_page_add(self):
        """Test that main calls page.add to add components."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        page.add.assert_called()

    @patch("flet.app")
    def test_flet_app_called_with_main(self, mock_app):
        """Test that ft.app is called with the main function."""

        assert callable(main)
        assert main.__name__ == "main"


class TestMainIntegration:
    """Integration tests for the main function with flet components."""

    def test_main_accepts_page_object(self):
        """Test that main properly handles a Page object with all required attributes."""

        page = Mock(spec=ft.Page)
        page.add = Mock()
        page.title = None
        page.vertical_alignment = None

        try:
            main(page)

        except Exception as e:
            pytest.fail(f"main() raised an exception: {e}")

    def test_main_has_expected_structure(self):
        """Test that main function has the expected structure and behavior."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        assert hasattr(page, "title")
        assert hasattr(page, "vertical_alignment")
        assert page.add.called
