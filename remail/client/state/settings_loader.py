"""Settings loader for initializing application state from database."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers import SettingsController
from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone
from remail.interfaces.email.services.user_service import UserService


def load_settings_into_state(app_state: AppState, page: ft.Page) -> None:
    """
    Load settings from database and populate app state.

    Args:
        app_state: The application state to populate
        page: The Flet page to apply theme to
    """
    settings_dto = SettingsController().get_settings()
    if settings_dto:
        try:
            app_state.theme_mode = ThemeMode(settings_dto.theme_mode)
            app_state.font_size = FontSize(settings_dto.font_size)
            app_state.font_family = FontFamily(settings_dto.font_family)
            app_state.language = Language(settings_dto.language)
            app_state.timezone = Timezone(settings_dto.timezone)
        except (ValueError, KeyError):
            pass

        app_state.desktop_notifications = settings_dto.desktop_notifications
        app_state.email_notifications = settings_dto.email_notifications
        app_state.quiet_hours = settings_dto.quiet_hours

    if app_state.theme_mode == ThemeMode.LIGHT:
        page.theme_mode = ft.ThemeMode.LIGHT
    elif app_state.theme_mode == ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.SYSTEM

    saved_users = UserService.get_all_users()
    app_state.connected_emails = saved_users
