from enum import Enum


class ConnectionSecurity(Enum):
    SSL_TLS = "ssl_tls"
    STARTTLS = "starttls"
    PLAIN = "plain"