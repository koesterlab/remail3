"""Task tray widget — renders active background tasks as a status bar."""

from __future__ import annotations

import flet as ft

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.client.state.task_progress import TaskProgress


def _task_row(task: TaskProgress) -> ft.Control:
    """Build a single task row containing a spinner/progress bar and a label.

    An indeterminate :class:`ft.ProgressRing` is shown when ``task.progress``
    is ``None``; otherwise a determinate :class:`ft.ProgressBar` is shown
    alongside a percentage label rendered in a fixed-width style to prevent
    layout shift as the number changes.

    Args:
        task: The task data to visualise.

    Returns:
        A :class:`ft.Row` control ready to be placed inside the tray column.
    """
    if task.progress is None:
        indicator: ft.Control = ft.ProgressRing(
            width=14,
            height=14,
            stroke_width=2,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        pct_label: ft.Control = ft.Container()  # empty spacer when indeterminate
    else:
        indicator = ft.ProgressBar(
            value=task.progress,
            width=80,
            height=4,
            color=ft.Colors.PRIMARY,
            bgcolor=ft.Colors.SURFACE_BRIGHT,
            border_radius=2,
        )
        pct_label = ft.Text(
            f"{task.progress * 100:.0f}%",
            size=11,
            color=ft.Colors.ON_SURFACE_VARIANT,
            # Monospaced style prevents layout shift as the number changes.
            font_family="monospace",
            width=32,
            text_align=ft.TextAlign.RIGHT,
        )

    return ft.Row(
        controls=[
            indicator,
            ft.Text(
                task.message,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT,
                expand=True,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
            ),
            pct_label,
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


class TaskTray(ft.AnimatedSwitcher):
    """Status bar that surfaces active background tasks.

    The widget observes ``MainAppStateProperties.RUNNING_TASKS`` and rebuilds
    its content whenever the task registry changes.  It is invisible (zero
    height) when no tasks are running and slides into view as soon as the first
    task is registered.

    Place this as the *last* control in the root :class:`ft.Column` so it acts
    as a persistent bottom bar across all views.

    Args:
        state: The shared application state instance.

    Example::

        tray = TaskTray(state)
        page_column = ft.Column([main_content, tray], expand=True)
    """

    def __init__(self, state: MainAppState) -> None:
        self._state = state

        super().__init__(
            content=ft.Container(),  # start empty
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=200,
            reverse_duration=150,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
        )

        state.register_observer(
            MainAppStateProperties.RUNNING_TASKS,
            self._on_tasks_changed,
        )

    def _on_tasks_changed(self, tasks: dict[str, TaskProgress]) -> None:
        """Rebuild the tray content whenever the task registry changes.

        Called from background threads via :meth:`MainAppState.trigger`, so
        ``self.page.update()`` is required to push the change to the client.

        Args:
            tasks: Current snapshot of the running-tasks registry.
        """
        self.content = self._build_content(tasks)
        try:
            self.update()
        except Exception:
            # Page not yet attached on the very first trigger. The content is
            # built from the state snapshot, so it will be correct on first
            # display; ignoring the failed update here is safe.
            pass

    def _build_content(self, tasks: dict[str, TaskProgress]) -> ft.Control:
        """Construct the visible tray container or an empty placeholder.

        Args:
            tasks: Current task registry snapshot.

        Returns:
            A styled :class:`ft.Container` with one row per task, or an
            invisible empty :class:`ft.Container` when the registry is empty.
        """
        if not tasks:
            return ft.Container(key="empty")  # unique key forces switcher animation

        rows = [_task_row(t) for t in tasks.values()]

        return ft.Container(
            key="tray",
            content=ft.Column(
                controls=rows,
                spacing=4,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            ),
        )
