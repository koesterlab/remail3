"""Tests for the remail application."""


def fetch_thread(*args, **kwargs):
    from .test_thread_data import fetch_thread as _fetch_thread

    return _fetch_thread(*args, **kwargs)


__all__ = ["fetch_thread"]
