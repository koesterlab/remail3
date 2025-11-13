"""Unit tests for permission_service."""

import pytest

from remail.interfaces.email.services.permission_service import PermissionService


class TestParsePermissionString:
    """Test suite for PermissionService.parse_permission_string method."""

    def test_parse_permission_string_full_permissions(self):
        """Test parsing full rwx permissions for all groups."""

        result = PermissionService.parse_permission_string("rwxrwxrwx")

        assert result == 0o777

    def test_parse_permission_string_no_permissions(self):
        """Test parsing no permissions."""

        result = PermissionService.parse_permission_string("---------")

        assert result == 0o000

    def test_parse_permission_string_owner_only(self):
        """Test parsing owner-only permissions."""

        result = PermissionService.parse_permission_string("rwx------")

        assert result == 0o700

    def test_parse_permission_string_read_only_all(self):
        """Test parsing read-only for all groups."""

        result = PermissionService.parse_permission_string("r--r--r--")

        assert result == 0o444

    def test_parse_permission_string_write_only_owner(self):
        """Test parsing write permission only for owner."""

        result = PermissionService.parse_permission_string("-w-------")

        assert result == 0o200

    def test_parse_permission_string_execute_only_all(self):
        """Test parsing execute-only for all groups."""

        result = PermissionService.parse_permission_string("--x--x--x")

        assert result == 0o111

    def test_parse_permission_string_common_file_0644(self):
        """Test parsing common file permissions 0644."""

        result = PermissionService.parse_permission_string("rw-r--r--")

        assert result == 0o644

    def test_parse_permission_string_common_file_0755(self):
        """Test parsing common executable permissions 0755."""

        result = PermissionService.parse_permission_string("rwxr-xr-x")

        assert result == 0o755

    def test_parse_permission_string_0600(self):
        """Test parsing owner read-write only 0600."""

        result = PermissionService.parse_permission_string("rw-------")

        assert result == 0o600

    def test_parse_permission_string_0764(self):
        """Test parsing 0764 permissions."""

        result = PermissionService.parse_permission_string("rwxrw-r--")

        assert result == 0o764

    def test_parse_permission_string_mixed_permissions(self):
        """Test parsing mixed permission patterns."""

        result = PermissionService.parse_permission_string("r-xr-----")

        assert result == 0o540

    def test_parse_permission_string_group_write_only(self):
        """Test parsing group write permission only."""

        result = PermissionService.parse_permission_string("----w----")

        assert result == 0o020

    def test_parse_permission_string_others_execute_only(self):
        """Test parsing others execute permission only."""

        result = PermissionService.parse_permission_string("------r-x")

        assert result == 0o005

    def test_parse_permission_string_invalid_too_short(self):
        """Test that string shorter than 9 characters raises ValueError."""
        with pytest.raises(ValueError, match="Permission string must be 9 characters, got 8"):
            PermissionService.parse_permission_string("rwxrwxrw")

    def test_parse_permission_string_invalid_too_long(self):
        """Test that string longer than 9 characters raises ValueError."""
        with pytest.raises(ValueError, match="Permission string must be 9 characters, got 10"):
            PermissionService.parse_permission_string("rwxrwxrwxr")

    def test_parse_permission_string_invalid_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Permission string must be 9 characters, got 0"):
            PermissionService.parse_permission_string("")

    def test_parse_permission_string_with_invalid_chars(self):
        """Test that invalid characters are treated as set permissions."""
        # Non-dash characters are treated as "permission set"

        result = PermissionService.parse_permission_string("abcdefghi")

        # All non-dash = all permissions set
        assert result == 0o777

    def test_parse_permission_string_mixed_case(self):
        """Test that uppercase letters are treated as set permissions."""

        result = PermissionService.parse_permission_string("RWX------")

        # Any non-dash is treated as permission set
        assert result == 0o700

    def test_parse_permission_string_numeric_chars(self):
        """Test that numeric characters are treated as set permissions."""

        result = PermissionService.parse_permission_string("123456789")

        # All non-dash = all permissions set
        assert result == 0o777

    def test_parse_permission_string_spaces(self):
        """Test that spaces are treated as set permissions."""

        result = PermissionService.parse_permission_string("   ------")

        # First 3 positions have non-dash = owner rwx
        assert result == 0o700

    def test_parse_permission_string_only_dashes(self):
        """Test string with only dashes."""

        result = PermissionService.parse_permission_string("---------")

        assert result == 0o000

    def test_parse_permission_string_0777_explicit(self):
        """Test explicit verification of 0777."""

        result = PermissionService.parse_permission_string("rwxrwxrwx")

        assert result == 0o777
        assert result == 511  # Decimal equivalent

    def test_parse_permission_string_calculation_owner_read(self):
        """Test individual permission calculation - owner read."""

        result = PermissionService.parse_permission_string("r--------")

        assert result == 0o400

    def test_parse_permission_string_calculation_owner_write(self):
        """Test individual permission calculation - owner write."""

        result = PermissionService.parse_permission_string("-w-------")

        assert result == 0o200

    def test_parse_permission_string_calculation_owner_execute(self):
        """Test individual permission calculation - owner execute."""

        result = PermissionService.parse_permission_string("--x------")

        assert result == 0o100

    def test_parse_permission_string_calculation_group_read(self):
        """Test individual permission calculation - group read."""

        result = PermissionService.parse_permission_string("---r-----")

        assert result == 0o040

    def test_parse_permission_string_calculation_others_write(self):
        """Test individual permission calculation - others write."""

        result = PermissionService.parse_permission_string("-------w-")

        assert result == 0o002
