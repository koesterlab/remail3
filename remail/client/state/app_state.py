"""Application state management."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from remail.client.views.view_router import ViewRouter
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import (
    FontFamily,
    FontSize,
    Language,
    MainView,
    SettingsSubView,
    ThemeMode,
    Timezone,
)

if TYPE_CHECKING:
    from remail.client.scheduler import Scheduler


@dataclass
class AppState:
    """Central application state container.

    Attributes:
        theme_mode: Current theme mode (light/dark/system)
        font_size: Selected font size
        font_family: Selected font family
        language: Application language
        timezone: User's timezone
        desktop_notifications: Whether desktop notifications are enabled
        email_notifications: Whether email notifications are enabled
        quiet_hours: Whether quiet hours mode is enabled
        current_views: Dictionary mapping main views to their current sub-views
        connected_emails: List of connected user DTOs
        email_schedulers: Dictionary mapping usernames to their schedulers
    """

    theme_mode: ThemeMode = ThemeMode.SYSTEM
    font_size: FontSize = FontSize.MEDIUM
    font_family: FontFamily = FontFamily.ARIAL
    language: Language = Language.ENGLISH
    timezone: Timezone = Timezone.EUROPE_BERLIN
    desktop_notifications: bool = True
    email_notifications: bool = True
    quiet_hours: bool = False
    current_views: dict[MainView, SettingsSubView | None] = field(default_factory=dict)
    router: ViewRouter | None = None
    connected_emails: list[UserDTO] = field(default_factory=list)
    email_schedulers: dict = field(default_factory=dict)

    def add_email_scheduler(self, username: str, scheduler: "Scheduler") -> None:
        """Add an email scheduler for an account.

        Args:
            username: The username of the account
            scheduler: The scheduler instance
        """

        self.email_schedulers[username] = scheduler

    def remove_email_scheduler(self, username: str) -> None:
        """Remove and stop an email scheduler.

        Args:
            username: The username of the account
        """

        scheduler = self.email_schedulers.pop(username, None)

        if scheduler:
            scheduler.stop()

    def stop_all_schedulers(self) -> None:
        """Stop all email schedulers. Call this on app close."""

        for scheduler in self.email_schedulers.values():
            scheduler.stop()

        self.email_schedulers.clear()

    def set_current_view(
        self, main_view: MainView, sub_view: SettingsSubView | None = None
    ) -> None:
        """Set the current sub-view for a main view.

        Args:
            main_view: The main view to set the sub-view for
            sub_view: The sub-view to set, or None for no sub-view
        """

        self.current_views[main_view] = sub_view

    def get_current_view(self, main_view: MainView) -> SettingsSubView | None:
        """Get the current sub-view for a main view.

        Args:
            main_view: The main view to get the sub-view for

        Returns:
            The current sub-view, or None if not set
        """

        return self.current_views.get(main_view)
