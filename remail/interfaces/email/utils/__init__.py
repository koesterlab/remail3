"""Utility functions for email operations."""

from remail.interfaces.email.utils.helpers import (
    create_email,
    parse_permission_string,
    save_attachment,
)

__all__ = ["create_email", "save_attachment", "parse_permission_string"]
