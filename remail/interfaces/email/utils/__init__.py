"""Utility functions for email operations."""

from remail.interfaces.email.services.attachment_service import save_attachment
from remail.interfaces.email.utils.helpers import (
    create_email,
    parse_permission_string,
)

__all__ = ["create_email", "save_attachment", "parse_permission_string"]
