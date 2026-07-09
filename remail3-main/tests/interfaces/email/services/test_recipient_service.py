from types import SimpleNamespace

from remail.interfaces.email.services.recipient_service import RecipientService

from remail.enums import RecipientKind


class DummyRecipient:
    """Minimal mock for recipient object used in Email.recipients."""

    def __init__(self, kind, email_address):
        self.kind = kind
        self.contact = SimpleNamespace(email_address=email_address)


class DummyEmail:
    """Mock Email object that mimics the model's structure."""

    def __init__(self, recipients):
        self.recipients = recipients


def test_split_recipients_correct_grouping():
    recipients = [
        DummyRecipient(RecipientKind.TO, "to1@example.com"),
        DummyRecipient(RecipientKind.CC, "cc1@example.com"),
        DummyRecipient(RecipientKind.BCC, "bcc1@example.com"),
        DummyRecipient(RecipientKind.TO, "to2@example.com"),
        DummyRecipient(RecipientKind.CC, "cc2@example.com"),
    ]
    mail = DummyEmail(recipients)
    to, cc, bcc = RecipientService.split_recipients(mail)

    assert to == ["to1@example.com", "to2@example.com"]
    assert cc == ["cc1@example.com", "cc2@example.com"]
    assert bcc == ["bcc1@example.com"]


def test_split_recipients_skips_missing_addresses():
    recipients = [
        DummyRecipient(RecipientKind.TO, None),
        DummyRecipient(RecipientKind.CC, ""),
        DummyRecipient(RecipientKind.BCC, "bcc@example.com"),
    ]
    mail = DummyEmail(recipients)
    to, cc, bcc = RecipientService.split_recipients(mail)

    assert to == []
    assert cc == []
    assert bcc == ["bcc@example.com"]


def test_split_recipients_ignores_unknown_kind():
    """If a recipient has an invalid or unexpected kind, it's ignored."""

    class FakeKind:
        pass

    recipients = [
        DummyRecipient(FakeKind(), "unknown@example.com"),
        DummyRecipient(RecipientKind.TO, "to@example.com"),
    ]
    mail = DummyEmail(recipients)
    to, cc, bcc = RecipientService.split_recipients(mail)

    assert to == ["to@example.com"]
    assert cc == []
    assert bcc == []


def test_split_recipients_empty_list_returns_empty():
    mail = DummyEmail([])
    to, cc, bcc = RecipientService.split_recipients(mail)

    assert to == []
    assert cc == []
    assert bcc == []
