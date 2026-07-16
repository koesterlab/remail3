import os
import webbrowser
from pathlib import Path


def open_file(path: str) -> bool:
    """
    Open a local file with the operating system's default application.

    Returns True when the file was handed off to the OS successfully,
    False when the path is empty, missing, or the OS refused to open it.
    """

    if not path:
        return False

    resolved = Path(path).resolve()
    if not resolved.exists():
        return False

    try:
        if os.name == "nt":
            os.startfile(str(resolved))  # type: ignore[attr-defined] # nosec B606
            return True
        return webbrowser.open(resolved.as_uri())
    except OSError:
        return False
