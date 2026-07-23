# task_tray

Central status-bar widget that surfaces active background tasks to the user.

## Purpose

Provides a persistent, non-intrusive overlay at the bottom of the application
window.  Each long-running process (email sync, LLM inference, attachment
upload, …) registers a `TaskProgress` entry in `MainAppState.RUNNING_TASKS`.
The tray reacts automatically: it appears when the first task starts and
disappears once the last one finishes.

## Files

| File | Role |
|---|---|
| `task_tray.py` | The Flet `Container` widget that renders the tray |
| `__init__.py` | Package exports |

## Usage

```python
from remail.client.widgets.task_tray import TaskTray

tray = TaskTray(state)
# Place tray as the last control in a ft.Column that fills the window.
```

To report progress from a background thread:

```python
# ... to add or update ...
state.report_task("my-task-id", "Still going…", progress=0.6)
# ... when done ...
state.remove_task("my-task-id")
```
