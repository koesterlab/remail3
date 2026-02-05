from datetime import datetime
from typing import Any

import remail.enums.connection_security
from remail import errors as ee
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import RecipientKind, ConnectionSecurity, AuthMethods
from remail.interfaces.email.protocols.imap import ImapProtocol
from remail.interfaces.email.services import ConversationService, ThreadService
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.user_service import UserService
from remail.models import Contact, Email, EmailReception


class EmailController:
    """Controller for email operations using IMAP protocol."""

    def check_credentials(
            self,
            imap_username: str,
            imap_host: str,
            imap_port: int,
            imap_password: str,
            imap_security: ConnectionSecurity,
            imap_method: AuthMethods,
            smtp_username: str,
            smtp_host: str,
            smtp_port: int,
            smtp_password: str,
            smtp_security: ConnectionSecurity,
            smtp_method: AuthMethods
    ):
        protocol = ImapProtocol(
            imap_username=imap_username,
            imap_host=imap_host,
            imap_port=imap_port,
            imap_password=imap_password,
            imap_method=imap_method,
            imap_security=imap_security,
            smtp_username=smtp_username,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_password=smtp_password,
            smtp_method=smtp_method,
            smtp_security=smtp_security
        )
        try:
            if protocol.test_connection():
                return protocol
        except Exception as _:
            pass
        return None
