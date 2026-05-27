from importlib import import_module

from .account_controller import AccountController
from .email_controller import EmailController
from .llm_controller import LLMController
from .settings_controller import SettingsController
from .thread_controller import ThreadController

__all__ = [
    "EmailController",
    "LLMController",
    "SettingsController",
]

_LAZY_IMPORTS = {
    "ConversationsController": ".conversations_controller",
    "EmailController": ".email_controller",
    "LLMController": ".llm_controller",
    "SettingsController": ".settings_controller",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module = import_module(f"{__name__}{_LAZY_IMPORTS[name]}")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
