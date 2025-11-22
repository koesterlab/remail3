"""Application state management."""

from dataclasses import dataclass, field

from remail.enums import (
    FontFamily,
    FontSize,
    Language,
    MainView,
    SettingsSubView,
    ThemeMode,
    Timezone,
)


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
    """

    theme_mode: ThemeMode = ThemeMode.SYSTEM
    font_size: FontSize = FontSize.MEDIUM
    font_family: FontFamily = FontFamily.ARIAL
    language: Language = Language.ENGLISH
    timezone: Timezone = Timezone.EUROPE_LONDON
    desktop_notifications: bool = True
    email_notifications: bool = True
    quiet_hours: bool = False
    current_views: dict[MainView, SettingsSubView | None] = field(default_factory=dict)

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
