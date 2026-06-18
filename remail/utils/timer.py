import time


class Timer:
    def __init__(self):
        self._start = time.monotonic()

    def elapsed(self) -> str:
        return f"{time.monotonic() - self._start:.3f}s"
