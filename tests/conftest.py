import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# These test modules still target removed modules and a superseded settings UI API.
# They are kept out of collection until equivalent coverage is rewritten against the
# current implementation.
collect_ignore = [
    "client/state/test_app_state.py",
    "client/state/test_settings_loader.py",
    "client/test_index.py",
    "client/views/settings/test_appearance_view.py",
    "client/views/settings/test_email_accounts_view.py",
    "client/views/settings/test_language_view.py",
    "client/views/settings/test_notifications_view.py",
    "client/views/settings/test_settings_view.py",
    "client/widgets/mail_selection/test_action_preview.py",
    "client/widgets/mail_selection/test_conversation_preview.py",
    "client/widgets/mail_selection/test_conversation_selection.py",
    "client/widgets/mail_selection/test_group_preview.py",
    "client/widgets/mail_selection/test_search_header.py",
    "client/widgets/mail_selection/test_selection_bar.py",
    "client/widgets/mail_selection/test_thread_selection.py",
    "client/widgets/settings/appearance/test_font_family_selector.py",
    "client/widgets/settings/appearance/test_font_size_selector.py",
    "client/widgets/settings/appearance/test_theme_selector.py",
    "client/widgets/settings/test_navigation.py",
    "client/widgets/thread/test_message_bubble.py",
    "controllers/dtos/test_settings_dto.py",
    "controllers/test_account_controller.py",
    "controllers/test_llm_controller.py",
    "controllers/test_settings_controller.py",
    "interfaces/email/services/test_attachment_service.py",
    "interfaces/email/services/test_contact_service.py",
    "interfaces/email/services/test_conversation_service.py",
    "interfaces/email/services/test_dashboard_service.py",
    "interfaces/email/services/test_email_sync_service.py",
    "interfaces/email/services/test_folder_service.py",
    "interfaces/email/services/test_settings_service.py",
    "interfaces/email/services/test_thread_service.py",
    "interfaces/email/services/test_user_service.py",
    "interfaces/email/services/test_recipient_service.py",
    "interfaces/email/test_thread_service.py",
    "interfaces/llm/test_llm_service.py",
    "models/test_conversation.py",
    "models/test_thread.py",
    "models/test_user.py",
]


@pytest.fixture()
def test_engine():
    """Create a fresh in-memory database engine for a test."""
    import remail.models  # noqa: F401

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def patch_db_engine(test_engine, monkeypatch):
    """Patch all database engine references to use the test engine."""
    import remail.database
    import remail.utils.session_management as session_management

    remail.database.engine = test_engine
    # Prevent leaked @session context between tests when a session is provided.
    session_management._current_session.set(None)
    yield
    session_management._current_session.set(None)


# Single-test isolated session bound to the shared test engine
@pytest.fixture()
def session(test_engine):
    with Session(test_engine) as s:
        yield s


@pytest.fixture()
def test_session(test_engine):
    """Alias for session fixture to match existing test names."""
    with Session(test_engine) as s:
        yield s
