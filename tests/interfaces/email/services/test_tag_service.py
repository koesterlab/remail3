"""Tests for TagService."""

from unittest.mock import MagicMock

import pytest

from remail.interfaces.email.services.tag_service import TagService


@pytest.fixture
def mock_imap_client():
    """Create a mock IMAP client."""

    return MagicMock()


@pytest.fixture
def tag_service(mock_imap_client):
    """Create a TagService instance."""

    return TagService(mock_imap_client)


class TestTagService:
    """Test suite for TagService."""

    def test_add_tag_custom_keyword(self, tag_service, mock_imap_client):
        """Test adding a custom tag (should be prefixed with $)."""

        tag_service.add_tag(123, "important")

        mock_imap_client.add_flags.assert_called_once_with([123], [b"$important"])

    def test_add_tag_with_dollar_prefix(self, tag_service, mock_imap_client):
        """Test adding a tag that already has $ prefix."""

        tag_service.add_tag(123, "$important")

        mock_imap_client.add_flags.assert_called_once_with([123], [b"$important"])

    def test_add_tag_standard_flag(self, tag_service, mock_imap_client):
        """Test adding a standard IMAP flag (should not be prefixed)."""

        tag_service.add_tag(123, "\\FLAGGED")

        mock_imap_client.add_flags.assert_called_once_with([123], [b"\\FLAGGED"])

    def test_add_tag_standard_flag_lowercase(self, tag_service, mock_imap_client):
        """Test adding a standard IMAP flag in lowercase."""

        tag_service.add_tag(123, "\\flagged")

        # Should still recognize it as standard flag
        mock_imap_client.add_flags.assert_called_once_with([123], [b"\\flagged"])

    def test_remove_tag_custom_keyword(self, tag_service, mock_imap_client):
        """Test removing a custom tag."""

        tag_service.remove_tag(123, "important")

        mock_imap_client.remove_flags.assert_called_once_with([123], [b"$important"])

    def test_remove_tag_with_dollar_prefix(self, tag_service, mock_imap_client):
        """Test removing a tag that already has $ prefix."""

        tag_service.remove_tag(123, "$important")

        mock_imap_client.remove_flags.assert_called_once_with([123], [b"$important"])

    def test_remove_tag_standard_flag(self, tag_service, mock_imap_client):
        """Test removing a standard IMAP flag."""

        tag_service.remove_tag(123, "\\FLAGGED")

        mock_imap_client.remove_flags.assert_called_once_with([123], [b"\\FLAGGED"])

    def test_get_tags_returns_custom_keywords(self, tag_service, mock_imap_client):
        """Test getting tags returns custom keywords and standard flags."""

        mock_imap_client.fetch.return_value = {
            123: {
                b"FLAGS": [b"$important", b"$work", b"\\SEEN", b"\\FLAGGED"],
            }
        }

        tags = tag_service.get_tags(123)

        assert "$important" in tags
        assert "$work" in tags
        assert "\\SEEN" in tags
        assert "\\FLAGGED" in tags
        assert len(tags) == 4

    def test_get_tags_no_flags(self, tag_service, mock_imap_client):
        """Test getting tags when email has no flags."""

        mock_imap_client.fetch.return_value = {
            123: {
                b"FLAGS": [],
            }
        }

        tags = tag_service.get_tags(123)

        assert tags == []

    def test_get_tags_uid_not_found(self, tag_service, mock_imap_client):
        """Test getting tags when UID doesn't exist."""

        mock_imap_client.fetch.return_value = {}

        tags = tag_service.get_tags(123)

        assert tags == []

    def test_search_by_tag_custom_keyword(self, tag_service, mock_imap_client):
        """Test searching by custom tag."""

        mock_imap_client.search.return_value = [123, 456, 789]

        uids = tag_service.search_by_tag("important")

        mock_imap_client.search.assert_called_once_with(["KEYWORD", "$important"])

        assert uids == [123, 456, 789]

    def test_search_by_tag_with_dollar_prefix(self, tag_service, mock_imap_client):
        """Test searching by tag that already has $ prefix."""

        mock_imap_client.search.return_value = [123]

        uids = tag_service.search_by_tag("$important")

        mock_imap_client.search.assert_called_once_with(["KEYWORD", "$important"])

        assert uids == [123]

    def test_search_by_tag_standard_flag(self, tag_service, mock_imap_client):
        """Test searching by standard flag."""

        mock_imap_client.search.return_value = [123, 456]

        uids = tag_service.search_by_tag("\\FLAGGED")

        mock_imap_client.search.assert_called_once_with(["KEYWORD", "\\FLAGGED"])
        assert uids == [123, 456]

    def test_search_by_tag_no_results(self, tag_service, mock_imap_client):
        """Test searching by tag with no results."""

        mock_imap_client.search.return_value = []

        uids = tag_service.search_by_tag("nonexistent")

        assert uids == []
