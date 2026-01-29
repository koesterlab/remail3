"""Async scheduler for periodic background tasks."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable


class Scheduler:
    """Scheduler for periodic background tasks.

    Runs a task on startup and then at regular intervals.
    Designed to work with Flet's event loop without blocking the UI.
    """

    def __init__(
        self,
        task: Callable[[], dict],
        sync_interval: int = 60,
        on_complete: Callable[[dict], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ):
        """
        Initialize the scheduler.

        Args:
            task: Callable that performs the task and returns a result dict
            sync_interval: Interval in seconds between runs (default: 60)
            on_complete: Callback when task completes successfully
            on_error: Callback when task fails
        """

        self.task = task
        self.sync_interval = sync_interval
        self.on_complete = on_complete
        self.on_error = on_error

        self._running = False
        self._task: asyncio.Task | None = None
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the scheduler.

        Creates a background thread with its own event loop to run
        tasks without blocking the main UI thread.
        """
        print("Starting scheduler")
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the scheduler.

        Gracefully stops the background task and thread.
        """
        print("Stopping Scheduler")
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        if self._loop and self._task:
            self._loop.call_soon_threadsafe(self._task.cancel)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        self._task = None
        self._thread = None
        self._loop = None

    def run_now(self) -> None:
        """Trigger an immediate run.

        Useful for manual refresh or initial sync.
        """

        if self._loop and self._running:
            asyncio.run_coroutine_threadsafe(self._do_task(), self._loop)

        else:
            threading.Thread(target=self._run_in_thread, daemon=True).start()

    def _run_async_loop(self) -> None:
        """Run the async event loop in a background thread."""

        self._loop = asyncio.new_event_loop()

        asyncio.set_event_loop(self._loop)

        try:
            self._task = self._loop.create_task(self._task_loop())
            self._loop.run_until_complete(self._task)

        except asyncio.CancelledError:
            pass

        finally:
            self._loop.close()

    async def _task_loop(self) -> None:
        """Main async loop that runs task periodically."""

        await self._do_task()

        while self._running and not self._stop_event.is_set():
            try:
                await asyncio.sleep(self.sync_interval)

                if self._running and not self._stop_event.is_set():
                    await self._do_task()

            except asyncio.CancelledError:
                break

    async def _do_task(self) -> None:
        """Execute task asynchronously."""

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.task)

            self._handle_result(result)

        except Exception as e:
            if self.on_error:
                self.on_error(str(e))

    def _run_in_thread(self) -> None:
        """Execute task synchronously in a thread."""

        try:
            result = self.task()

            self._handle_result(result)
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))

    def _handle_result(self, result: dict) -> None:
        """Handle the result and call appropriate callbacks."""

        if result.get("status") == "success":
            if self.on_complete:
                self.on_complete(result)

        else:
            if self.on_error:
                self.on_error(result.get("message", "Unknown error"))

    @property
    def is_running(self) -> bool:
        """Check if the scheduler is currently running."""

        return self._running
