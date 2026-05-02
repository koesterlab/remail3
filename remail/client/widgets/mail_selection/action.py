from collections.abc import Callable
from dataclasses import dataclass

import flet


@dataclass
class Action:
    title: str
    secondary: str
    on_executed: Callable[[], None]
    color: flet.Colors
    icon: flet.IconData
