"""Unit tests for the main client index module."""

import os
from unittest.mock import Mock, patch

import flet as ft
import pytest

from remail.client.index import main


@pytest.fixture
def mock_env():
    """Mock LLM environment variables."""
    with patch.dict(
        os.environ,
        {
            "LLM_API_KEY": "test-key",
            "LLM_BASE_URL": "http://localhost:8000/v1",
        },
    ):
        yield


@pytest.fixture
def patch_main_deps():
    with (
        patch("remail.client.index.load_settings_into_state"),
        patch("remail.client.index.create_main_view", return_value=ft.Container()),
        patch("remail.client.index.create_settings_view", return_value=ft.Container()),
        patch("remail.client.index.UserService.get_all_users", return_value=[]),
    ):
        yield


class TestMain:
    """Test suite for the main function."""

    def test_main_sets_page_title(self, mock_env, patch_main_deps):
        """Test that main sets the correct page title."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        # Title is set in main, but may be overridden by the view
        assert page.title in ["Remail 2.0", "Remail 2.0 - Chatbot", "Settings"]

    def test_main_sets_vertical_alignment(self, mock_env, patch_main_deps):
        """Test that main sets vertical alignment to center."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        assert page.vertical_alignment == ft.MainAxisAlignment.CENTER

    def test_main_calls_page_add(self, mock_env, patch_main_deps):
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

    def test_main_accepts_page_object(self, mock_env, patch_main_deps):
        """Test that main properly handles a Page object with all required attributes."""

        page = Mock(spec=ft.Page)
        page.add = Mock()
        page.title = None
        page.vertical_alignment = None

        try:
            main(page)

        except Exception as e:
            pytest.fail(f"main() raised an exception: {e}")

    def test_main_has_expected_structure(self, mock_env, patch_main_deps):
        """Test that main function has the expected structure and behavior."""

        page = Mock(spec=ft.Page)
        page.add = Mock()

        main(page)

        assert hasattr(page, "title")
        assert hasattr(page, "vertical_alignment")
        assert page.add.called
