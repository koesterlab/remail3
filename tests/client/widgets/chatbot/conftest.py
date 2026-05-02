from unittest.mock import Mock

import pytest

from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone


@pytest.fixture(autouse=True)
def patch_chatbot_settings(monkeypatch):
    settings = SettingsDTO(
        id=1,
        theme_mode=ThemeMode.SYSTEM,
        font_size=FontSize.MEDIUM,
        font_family=FontFamily.ARIAL,
        language=Language.ENGLISH,
        timezone=Timezone.EUROPE_BERLIN,
        desktop_notifications=True,
        email_notifications=True,
        quiet_hours=False,
        llm_url="http://llm",
        llm_key="key",
    )
    controller = Mock()
    controller.get_settings.return_value = settings
    monkeypatch.setattr(
        "remail.client.widgets.chatbot.chatbot.SettingsController",
        lambda: controller,
    )
