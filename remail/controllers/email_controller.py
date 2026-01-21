"""Email controller for managing email operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from remail import errors as ee
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import ConversationType, RecipientKind
from remail.interfaces.email.protocols.imap import ImapProtocol
from remail.interfaces.email.services import ConversationService, ThreadService
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.user_service import UserService
from remail.models import Contact, Email, EmailReception


class EmailController:
    """Controller for email operations using IMAP protocol."""

    @classmethod
    def from_id(cls, account_id: int):
        user: UserDTO = next(filter(lambda u: u.id == account_id, UserService.get_all_users()))
        return EmailController(username=user.email, password=user.password, host=user.host)

    def __init__(self, username: str, password: str, host: str):
        """
        Initialize email controller.

        Args:
            username: Email username/address
            password: Email password
            host: IMAP/SMTP server hostname
        """

        self.protocol = ImapProtocol(username=username, password=password, host=host)
        self.thread_service = ThreadService()

    def login(self) -> dict[str, Any]:
        """
        Authenticate user with IMAP server.

        Returns:
            Dict with status and message
        """

        try:
            self.protocol.login()

            return {
                "status": "success",
                "message": "Successfully logged in",
                "logged_in": True,
            }

        except ee.InvalidLoginData:
            return {
                "status": "error",
                "message": "Invalid login credentials",
                "logged_in": False,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Login failed: {str(e)}",
                "logged_in": False,
            }

    def logout(self) -> dict[str, Any]:
        """
        Logout from IMAP server.

        Returns:
            Dict with status and message
        """

        try:
            self.protocol.logout()

            return {
                "status": "success",
                "message": "Successfully logged out",
                "logged_in": False,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Logout failed: {str(e)}",
                "logged_in": False,
            }

    def send_email(
        self,
        subject: str,
        body: str,
        attachments: list[str] | None = None,
        thread_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Send an email.

        Args:
            subject: Email subject
            body: Email body
            attachments: List of attachment filenames
            thread_id: Thread ID (used when recipients are inferred from a thread)

        Returns:
            Dict with status and message
        """

        try:
            if thread_id is None:
                raise ValueError("Invalid thread ID provided.")

            thread = ThreadService().get_thread_by_id(thread_id)

            if thread is None:
                raise ValueError("Thread with the specified ID does not exist.")

            resolved_to = [rec.email for rec in thread.contacts]

            email = self._create_email_model(
                subject=subject,
                body=body,
                to=resolved_to,
                attachments=attachments,
                thread_id=thread_id,
            )

            self.protocol.send_email(email)

            return {
                "status": "success",
                "message": "Email sent successfully",
                "email": self._serialize_email(email),
            }

        except ee.NotLoggedIn:
            return {
                "status": "error",
                "message": "Not logged in",
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
            }

    def send_email_new_thread(
        self, subject: str, body: str, conversation_id: int, attachments: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Send an email starting a new thread.

        Args:
            subject: Email subject
            body: Email body
            conversation_id: Conversation ID to associate the new thread with
            attachments: List of attachment filenames

        Returns:
            Dict with status and message
        """

        try:
            conversation = ConversationService().get_conversation_by_id(conversation_id)

            if conversation is None:
                raise ValueError("Invalid conversation ID provided.")

            thread = ThreadService().create_thread(
                title=subject,
                conversation_id=conversation_id,
            )

            if thread.id is None:
                raise ValueError("Failed to create thread.")

            to = [contact["email"] for contact in conversation["contacts"]]

            email = self._create_email_model(
                subject=subject,
                body=body,
                to=to,
                attachments=attachments or [],
                thread_id=thread.id,
            )

            self.protocol.send_email(email)

            return {
                "status": "success",
                "message": "Email sent successfully",
                "email": self._serialize_email(email),
                "thread_id": thread.id,
                "conversation_id": conversation_id,
            }

        except ee.NotLoggedIn:
            return {
                "status": "error",
                "message": "Not logged in",
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
            }

    def send_email_new_conversation(
        self, contact_ids: list[int], subject: str, body: str, attachments: list[str] | None = None
    ) -> dict[str, Any]:
        try:
            contacts: list[Contact] = []

            for contact_id in contact_ids:
                contact = ContactService().get_contact_by_id(contact_id)

                if contact is None:
                    raise ValueError(f"Contact ID {contact_id} not found.")

                contacts.append(contact)

            if not contacts:
                raise ValueError("No recipients provided.")

            conversation = ConversationService().create_conversation(
                conversation_type=ConversationType.GROUP,
                custom_name=subject,
                contacts=contacts,
            )

            if conversation.id is None:
                raise ValueError("Failed to create conversation.")

            thread = ThreadService().create_thread(
                title=subject,
                conversation_id=conversation.id,
            )

            if thread.id is None:
                raise ValueError("Failed to create thread.")

            to = [rec.email_address for rec in contacts]

            email = self._create_email_model(
                subject=subject,
                body=body,
                to=to,
                attachments=attachments or [],
                thread_id=thread.id,
            )

            self.protocol.send_email(email)

            return {
                "status": "success",
                "message": "Email sent successfully",
                "email": self._serialize_email(email),
                "thread_id": thread.id,
                "conversation_id": conversation.id,
            }

        except ee.NotLoggedIn:
            return {
                "status": "error",
                "message": "Not logged in",
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
            }

    def delete_email(self, message_id: str, hard_delete: bool = False) -> dict[str, Any]:
        """
        Delete an email.

        Args:
            message_id: Message ID of the email to delete
            hard_delete: If True, permanently delete; otherwise move to trash

        Returns:
            Dict with status and message
        """

        try:
            self.protocol.delete_email(message_id=message_id, hard_delete=hard_delete)

            return {
                "status": "success",
                "message": f"Email {'permanently deleted' if hard_delete else 'moved to trash'}",
                "message_id": message_id,
                "hard_delete": hard_delete,
            }

        except ee.NotLoggedIn:
            return {
                "status": "error",
                "message": "Not logged in",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete email: {str(e)}",
            }

    def tag_email(self, message_id: str, tag: str, remove: bool = False) -> dict[str, Any]:
        """
        Add or remove a tag from an email.

        Args:
            message_id: Message ID of the email to tag
            tag: Tag name to add or remove
            remove: If True, remove the tag; otherwise add it

        Returns:
            Dict with status, message, and tag details
        """

        try:
            self.protocol.tag_email(message_id=message_id, tag=tag, remove=remove)

            return {
                "status": "success",
                "message": f"Tag '{tag}' {'removed from' if remove else 'added to'} email",
                "message_id": message_id,
                "tag": tag,
                "action": "remove" if remove else "add",
            }

        except ee.NotLoggedIn:
            return {
                "status": "error",
                "message": "Not logged in",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to tag email: {str(e)}",
            }

    def _create_email_model(
        self,
        subject: str,
        body: str,
        to: list[str] | None = None,
        attachments: list[str] | None = None,
        thread_id: int | None = None,
    ) -> Email:
        """
        Create an Email model instance from parameters.

        Args:
            subject: Email subject
            body: Email body
            to: TO recipients
            attachments: Attachment filenames
            thread_id: Thread ID (optional for sending)

        Returns:
            Email model instance
        """

        from remail.models import Attachment

        resolved_thread_id = thread_id if thread_id is not None else 0

        sender = Contact(
            name=self.protocol.user_username or "Unknown",
            email_address=self.protocol.user_username or "",
        )

        email = Email(
            subject=subject,
            body=body,
            sent_at=datetime.now(),
            sender=sender,
            thread_id=resolved_thread_id,
        )

        recipients: list[EmailReception] = []

        for addr in to or []:
            contact = Contact(name=addr, email_address=addr)

            recipients.append(
                EmailReception(
                    kind=RecipientKind.TO,
                    email=email,
                    contact=contact,
                )
            )

        email.recipients = recipients

        if attachments:
            email.attachments = [Attachment(filename=fname, email=email) for fname in attachments]

        return email

    def _serialize_email(self, email: Email) -> dict[str, Any]:
        """
        Serialize an Email model to dict.

        Args:
            email: Email model instance

        Returns:
            Dict representation of email
        """

        return {
            "id": email.id,
            "subject": email.subject,
            "body": email.body,
            "sent_at": email.sent_at.isoformat() if email.sent_at else None,
            "sender": {
                "name": email.sender.name if email.sender else None,
                "email": email.sender.email_address if email.sender else None,
            },
            "recipients": [
                {
                    "kind": rec.kind.value,
                    "name": rec.contact.name,
                    "email": rec.contact.email_address,
                }
                for rec in email.recipients
            ]
            if email.recipients
            else [],
            "attachments": [att.filename for att in email.attachments] if email.attachments else [],
        }
