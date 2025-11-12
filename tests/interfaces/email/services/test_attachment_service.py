"""Unit tests for attachment service."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from remail.interfaces.email.services.attachment_service import save_attachment


class TestSaveAttachment:
    """Test suite for the save_attachment function."""

    @pytest.fixture
    def temp_attachments_dir(self, tmp_path):
        """Create a temporary attachments directory for testing."""
        attachments_dir = tmp_path / "remail" / "database" / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)
        
        # Patch the function to use our temp directory
        with patch("remail.interfaces.email.services.attachment_service.os.path.abspath") as mock_abspath:
            mock_abspath.return_value = str(attachments_dir)
            yield attachments_dir

    def test_save_attachment_basic(self, temp_attachments_dir):
        """Test basic attachment saving with valid inputs."""
        filename = "test.txt"
        content = b"Test content"
        message_id = "msg123"
        
        filepath = save_attachment(filename, content, message_id)
        
        # Verify file was created
        assert os.path.exists(filepath)
        
        # Verify content is correct
        with open(filepath, "rb") as f:
            assert f.read() == content
        
        # Verify filepath structure
        assert "msg123" in filepath
        assert filepath.endswith("test.txt")

    def test_save_attachment_with_extension(self, temp_attachments_dir):
        """Test saving attachment with various file extensions."""
        test_cases = [
            ("document.pdf", b"PDF content"),
            ("image.jpg", b"JPG content"),
            ("archive.zip", b"ZIP content"),
            ("data.json", b'{"key": "value"}'),
        ]
        
        for filename, content in test_cases:
            filepath = save_attachment(filename, content, "msg_ext_test")
            assert os.path.exists(filepath)
            assert filepath.endswith(os.path.splitext(filename)[1])
            
            with open(filepath, "rb") as f:
                assert f.read() == content

    def test_save_attachment_sanitizes_filename(self, temp_attachments_dir):
        """Test that filenames are properly sanitized."""
        dangerous_filenames = [
            ("../../etc/passwd.txt", "etcpasswd.txt"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("file@#$%^&*.txt", "file.txt"),
        ]
        
        for dangerous_name, expected_safe_part in dangerous_filenames:
            content = b"Test content"
            filepath = save_attachment(dangerous_name, content, "msg_sanitize")
            
            # Verify the file was saved securely
            assert os.path.exists(filepath)
            assert ".." not in filepath
            assert "msg_sanitize" in filepath

    def test_save_attachment_truncates_long_filename(self, temp_attachments_dir):
        """Test that very long filenames are truncated."""
        # Create a filename longer than 50 characters (before extension)
        long_name = "a" * 100 + ".txt"
        content = b"Test content"
        
        filepath = save_attachment(long_name, content, "msg_long")
        
        assert os.path.exists(filepath)
        # The name part should be truncated to 50 chars
        basename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(basename)[0]
        assert len(name_without_ext) <= 50

    def test_save_attachment_removes_dots_from_name(self, temp_attachments_dir):
        """Test that dots are removed from filename (except extension)."""
        filename = "my.file.with.dots.txt"
        content = b"Test content"
        
        filepath = save_attachment(filename, content, "msg_dots")
        
        assert os.path.exists(filepath)
        basename = os.path.basename(filepath)
        # Should have removed internal dots but kept extension
        assert basename.endswith(".txt")
        name_part = os.path.splitext(basename)[0]
        assert "." not in name_part

    def test_save_attachment_creates_message_directory(self, temp_attachments_dir):
        """Test that the message-specific directory is created."""
        filepath = save_attachment("test.txt", b"content", "new_message_id")
        
        # Verify the message directory was created
        message_dir = os.path.dirname(filepath)
        assert os.path.exists(message_dir)
        assert "new_message_id" in message_dir

    def test_save_attachment_sanitizes_message_id(self, temp_attachments_dir):
        """Test that message IDs with dots are sanitized."""
        message_id = "msg.with.dots@example.com"
        filepath = save_attachment("test.txt", b"content", message_id)
        
        # Dots should be replaced with underscores in directory name
        assert os.path.exists(filepath)
        assert "msg_with_dots" in filepath or "msgwithdotsexamplecom" in filepath

    def test_save_attachment_exceeds_size_limit(self, temp_attachments_dir):
        """Test that files exceeding size limit raise BufferError."""
        # Create content larger than 200 MB
        large_content = b"x" * (200 * 1024 * 1024 + 1)
        
        with pytest.raises(BufferError, match="File size exceeds limit"):
            save_attachment("large.txt", large_content, "msg_large")

    def test_save_attachment_at_size_limit(self, temp_attachments_dir):
        """Test that files at exactly the size limit are accepted."""
        # Create content at exactly 200 MB
        max_content = b"x" * (200 * 1024 * 1024)
        
        filepath = save_attachment("max_size.txt", max_content, "msg_max")
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) == 200 * 1024 * 1024

    def test_save_attachment_empty_filename_after_sanitization(self, temp_attachments_dir):
        """Test that completely invalid filenames raise ValueError."""
        invalid_filenames = [
            "...",
            "///",
            "   ",
            "",
        ]
        
        for invalid_name in invalid_filenames:
            with pytest.raises(ValueError, match="Invalid filename"):
                save_attachment(invalid_name, b"content", "msg_invalid")

    def test_save_attachment_preserves_content(self, temp_attachments_dir):
        """Test that binary content is preserved exactly."""
        # Test with various binary content
        binary_contents = [
            b"\x00\x01\x02\x03\x04",
            b"\xff\xfe\xfd\xfc",
            bytes(range(256)),
        ]
        
        for idx, content in enumerate(binary_contents):
            filepath = save_attachment(f"binary_{idx}.bin", content, f"msg_binary_{idx}")
            
            with open(filepath, "rb") as f:
                saved_content = f.read()
                assert saved_content == content

    def test_save_attachment_sets_correct_permissions(self, temp_attachments_dir):
        """Test that file permissions are set to 764."""
        filepath = save_attachment("perms.txt", b"content", "msg_perms")
        
        # Get file permissions
        stat_info = os.stat(filepath)
        permissions = oct(stat_info.st_mode)[-3:]
        
        assert permissions == "764"

    def test_save_attachment_overwrites_existing_file(self, temp_attachments_dir):
        """Test that saving with the same filename overwrites the previous file."""
        filename = "overwrite.txt"
        message_id = "msg_overwrite"
        
        # Save first version
        filepath1 = save_attachment(filename, b"version 1", message_id)
        
        # Save second version with same name
        filepath2 = save_attachment(filename, b"version 2", message_id)
        
        # Should be the same path
        assert filepath1 == filepath2
        
        # Should contain the latest content
        with open(filepath2, "rb") as f:
            assert f.read() == b"version 2"

    def test_save_attachment_multiple_files_same_message(self, temp_attachments_dir):
        """Test saving multiple attachments for the same message."""
        message_id = "msg_multi"
        
        filepath1 = save_attachment("file1.txt", b"content 1", message_id)
        filepath2 = save_attachment("file2.txt", b"content 2", message_id)
        filepath3 = save_attachment("file3.pdf", b"content 3", message_id)
        
        # All should exist
        assert os.path.exists(filepath1)
        assert os.path.exists(filepath2)
        assert os.path.exists(filepath3)
        
        # All should be in the same directory
        assert os.path.dirname(filepath1) == os.path.dirname(filepath2)
        assert os.path.dirname(filepath2) == os.path.dirname(filepath3)

    def test_save_attachment_unicode_filename(self, temp_attachments_dir):
        """Test handling of unicode characters in filenames."""
        unicode_names = [
            "文档.txt",
            "документ.pdf",
            "café_menu.jpg",
        ]
        
        for filename in unicode_names:
            content = b"Unicode test content"
            filepath = save_attachment(filename, content, "msg_unicode")
            
            # Should save successfully (werkzeug will handle unicode)
            assert os.path.exists(filepath)
            
            with open(filepath, "rb") as f:
                assert f.read() == content

    def test_save_attachment_empty_content(self, temp_attachments_dir):
        """Test saving attachment with empty content."""
        filepath = save_attachment("empty.txt", b"", "msg_empty")
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) == 0

    def test_save_attachment_whitespace_stripped_from_filename(self, temp_attachments_dir):
        """Test that leading/trailing whitespace is stripped from filename."""
        filename = "  spaces.txt  "
        filepath = save_attachment(filename, b"content", "msg_spaces")
        
        assert os.path.exists(filepath)
        basename = os.path.basename(filepath)
        assert not basename.startswith(" ")
        assert not basename.endswith(" ")
