# remail

ReMail - Email management with AI-powered features

## For New Developers

### Getting Started

This project uses [Pixi](https://pixi.sh) for dependency management and task execution. Pixi provides a fast, cross-platform package manager that handles both conda and PyPI packages.

#### Prerequisites

Install Pixi:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

#### Setup

Clone and install dependencies:

```bash
git clone https://github.com/koesterlab/remail2.git
cd remail2
pixi install
```

### Available Commands

The project includes several pixi tasks defined in `pixi.toml`:

- **`pixi run test`** - Run the test suite with pytest
- **`pixi run lint`** - Check code for linting errors with Ruff
- **`pixi run format-lint`** - Apply Ruff auto-fixes (imports, lint rules)
- **`pixi run format-code`** - Run Ruff formatter only
- **`pixi run format`** - Run both `format-lint` and `format-code` for a one-command auto-fix
- **`pixi run format-check`** - Check formatting and linting without making changes (used in CI)
- **`pixi run typecheck`** - Run mypy on the `remail` package with `--explicit-package-bases`
- **`pixi run deadcode`** - Identify unused code paths with Vulture (legacy-heavy modules are excluded)
- **`pixi run security`** - Execute Bandit security scans (legacy-heavy modules are excluded)

### Development Workflow

1. Make your changes
2. Format your code: `pixi run format`
3. Run tests: `pixi run test`
4. Create a pull request

### CI/CD Workflows

The project uses GitHub Actions for automated quality checks:

#### Code Quality (`.github/workflows/code-quality.yml`)

Runs on all pull requests to `main`:

- ✅ Runs test suite
- ✅ Checks code linting
- ✅ Verifies code formatting and import organization
- ✅ Runs mypy type checks
- ✅ Executes Vulture for dead code detection
- ✅ Executes Bandit security scan

#### Auto-assign Author (`.github/workflows/auto-assign-author.yml`)

Automatically assigns pull requests to their author for tracking.

#### Dependabot Auto-merge (`.github/workflows/dependabot-auto-merge.yml`)

Automatically approves and merges Dependabot pull requests for patch and minor version updates.

### Tech Stack

- **Python 3.12+**
- **Database**: SQLite with SQLModel ORM
- **Frontend**: Streamlit / Flet
- **AI/LLM**: LlamaIndex, ChromaDB for RAG, Hugging Face embeddings
- **Email**: IMAP and Exchange protocol support
- **Code Quality**: Ruff (linting & formatting), pytest (testing)

### Utils

- `remail/util/request.py` – `RequestBuilder` offers an immutable, fluent API for building `requests` calls, including helpers for headers, auth, payloads, and sending via shared sessions.
- `tests/utils/test_request.py` – Demonstrates usage patterns and guards edge cases such as cloning builders, attaching files, and propagating cookies.

## Email Controller

The `EmailController` provides a high-level interface for managing email operations using the IMAP protocol.

### Usage Example

```python
from remail.controllers import EmailController
from datetime import datetime, UTC

# Initialize the controller
controller = EmailController(
    username="user@example.com",
    password="your_password",
    host="imap.example.com"
)

# 1. Login
result = controller.login()
print(result)
# {
#     "status": "success",
#     "message": "Successfully logged in",
#     "logged_in": True
# }

# 2. Fetch all emails
result = controller.fetch_emails()
print(result)
# {
#     "status": "success",
#     "message": "Fetched 5 email(s)",
#     "count": 5,
#     "emails": [
#         {
#             "id": 1,
#             "subject": "Hello",
#             "body": "Email body",
#             "sent_at": "2025-11-13T10:30:00+00:00",
#             "sender": {
#                 "name": "John Doe",
#                 "email": "john@example.com"
#             },
#             "recipients": [
#                 {
#                     "kind": "to",
#                     "name": "recipient@example.com",
#                     "email": "recipient@example.com"
#                 }
#             ],
#             "attachments": ["file.pdf"]
#         },
#         ...
#     ]
# }

# Fetch emails with filters
result = controller.fetch_emails(
    folder="INBOX",
    since=datetime(2025, 11, 1, tzinfo=UTC),
    flags=["UNSEEN"]  # Only unread emails
)

# 3. Send an email
result = controller.send_email(
    subject="Test Email",
    body="This is a test email",
    to=["recipient1@example.com", "recipient2@example.com"],
    cc=["cc@example.com"],
    bcc=["bcc@example.com"],
    attachments=["document.pdf", "image.jpg"]
)
print(result)
# {
#     "status": "success",
#     "message": "Email sent successfully",
#     "email": {...}
# }

# 4. Delete an email
result = controller.delete_email(
    message_id="<msg123@example.com>",
    hard_delete=False  # Move to trash (default)
)
print(result)
# {
#     "status": "success",
#     "message": "Email moved to trash",
#     "message_id": "<msg123@example.com>",
#     "hard_delete": False
# }

# Permanently delete
result = controller.delete_email(
    message_id="<msg456@example.com>",
    hard_delete=True
)
print(result)
# {
#     "status": "success",
#     "message": "Email permanently deleted",
#     "message_id": "<msg456@example.com>",
#     "hard_delete": True
# }

# 5. Logout
result = controller.logout()
print(result)
# {
#     "status": "success",
#     "message": "Successfully logged out",
#     "logged_in": False
# }
```

### API Methods

#### `login() -> dict`
Authenticate with the IMAP server.

**Returns:**
```python
{
    "status": "success" | "error",
    "message": str,
    "logged_in": bool
}
```

#### `logout() -> dict`
Logout from the IMAP server.

**Returns:**
```python
{
    "status": "success" | "error",
    "message": str,
    "logged_in": bool
}
```

#### `fetch_emails(folder=None, since=None, flags=None) -> dict`
Fetch emails from the server.

**Parameters:**
- `folder` (str | None): Specific folder to fetch from (None = all folders)
- `since` (datetime | None): Only fetch emails after this datetime
- `flags` (list[str] | None): IMAP search flags (e.g., ["UNSEEN"])

**Returns:**
```python
{
    "status": "success" | "error",
    "message": str,
    "count": int,
    "emails": [
        {
            "id": int,
            "subject": str,
            "body": str,
            "sent_at": str,  # ISO format
            "sender": {"name": str, "email": str},
            "recipients": [{"kind": str, "name": str, "email": str}],
            "attachments": [str]
        }
    ]
}
```

#### `send_email(subject, body, to=None, cc=None, bcc=None, attachments=None) -> dict`
Send an email.

**Parameters:**
- `subject` (str): Email subject
- `body` (str): Email body
- `to` (list[str] | None): List of TO recipients
- `cc` (list[str] | None): List of CC recipients
- `bcc` (list[str] | None): List of BCC recipients
- `attachments` (list[str] | None): List of attachment filenames

**Returns:**
```python
{
    "status": "success" | "error",
    "message": str,
    "email": {...}  # Serialized email on success
}
```

#### `delete_email(message_id, hard_delete=False) -> dict`
Delete an email.

**Parameters:**
- `message_id` (str): Message ID of the email to delete
- `hard_delete` (bool): If True, permanently delete; otherwise move to trash

**Returns:**
```python
{
    "status": "success" | "error",
    "message": str,
    "message_id": str,  # On success
    "hard_delete": bool  # On success
}
```

### Error Handling

All methods return a dictionary with a `status` field that can be either `"success"` or `"error"`. When an error occurs, the `message` field contains details about the error.

Common error scenarios:
- **Not logged in**: Attempting operations without calling `login()` first
- **Invalid credentials**: Wrong username/password during login
- **No recipients**: Sending email without any recipients
- **Network errors**: Connection issues with the server

Example error response:
```python
{
    "status": "error",
    "message": "Not logged in"
}
```
