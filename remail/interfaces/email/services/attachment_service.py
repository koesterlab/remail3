import os

from sqlmodel import Session
from werkzeug.utils import secure_filename

from remail.models import Email
from remail.utils.session_management import session


@session
def save_attachment(filename: str, content: bytes, message: Email | str, session: Session) -> str:
    """
    Safely save an email attachment to disk.

    Args:
        filename: Original filename
        content: File content as bytes
        message: Owning Email message or message id

    Returns:
        Absolute path to saved file

    Raises:
        BufferError: If file size exceeds limit
        ValueError: If filename is invalid
    """

    attachments_dir = os.path.abspath(os.path.join("remail", "database", "attachments"))
    message_id = message.message_id if isinstance(message, Email) else message
    message_dir = os.path.join(attachments_dir, secure_filename(message_id or "").replace(".", "_"))
    max_size = 200 * 1024 * 1024  # 200 MB limit

    if len(content) > max_size:
        raise BufferError(f"File size exceeds limit of {max_size} bytes")

    os.makedirs(message_dir, exist_ok=True)

    name, ext = os.path.splitext(filename)
    sanitized_name = name.replace(".", "")[:50] + ext
    safe_name = secure_filename(sanitized_name.strip())

    if not safe_name:
        raise ValueError("Invalid filename")

    filepath = os.path.join(message_dir, safe_name)

    with open(filepath, "wb") as f:
        f.write(content)

    # Set permissions: rw-r--r-- (644)
    os.chmod(filepath, 0o644)

    return filepath
