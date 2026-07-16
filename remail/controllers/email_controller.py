from remail.enums import AuthMethods, ConnectionSecurity
from remail.interfaces.email.protocols.imap import ImapProtocol


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
        smtp_method: AuthMethods,
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
            smtp_security=smtp_security,
        )
        imap_ok = False
        smtp_ok = False

        try:
            imap_ok = protocol.test_imap_connection()
        except Exception as ex:
            imap_ok = False


        try:
            smtp_ok = protocol.test_smtp_connection()
        except Exception as ex:
            smtp_ok = False



        return {
            "protocol": protocol if imap_ok and smtp_ok else None,
            "imap_ok": imap_ok,
            "smtp_ok": smtp_ok,
        }