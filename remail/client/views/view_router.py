from collections.abc import Callable

import flet as ft

from remail.enums import MainView


class ViewRouter:
    """Router for managing main application views."""

    def __init__(self, page: ft.Page, app_state: "AppState"):  # type: ignore # noqa: F821   # sonst circular import
        self.page = page
        self.app_state = app_state

        self._view_registry: dict[MainView, Callable] = {}

    def load_view(self, view: MainView) -> ft.Container:
        """Load and return the specified view.

        Args:
            view: The main view to load

        Returns:
            The view container

        Raises:
            ValueError: If the view is not registered
        """

        if view not in self._view_registry:
            raise ValueError(f"View {view} is not registered")

        view_creator = self._view_registry[view]

        return view_creator(self.page, self.app_state)

    def register_view(self, view: MainView, view_creator: Callable) -> None:
        """Register a new view creator.

        Args:
            view: The main view enum
            view_creator: Function that creates the view, signature: (page, app_state) -> Container
        """

        self._view_registry[view] = view_creator
