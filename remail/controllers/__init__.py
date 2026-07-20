from importlib import import_module

__all__ = [
    "AccountController",
    "ConversationsController",
    "EmailController",
    "LLMController",
    "SettingsController",
    "ThreadController",
]

_LAZY_IMPORTS = {
    "AccountController": ".account_controller",
    "ConversationsController": ".conversations_controller",
    "EmailController": ".email_controller",
    "LLMController": ".llm_controller",
    "SettingsController": ".settings_controller",
    "ThreadController": ".thread_controller",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module = import_module(f"{__name__}{_LAZY_IMPORTS[name]}")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
