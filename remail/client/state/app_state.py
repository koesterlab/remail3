from dataclasses import dataclass, field


@dataclass
class AppState:
    theme_mode: str = "system"  # "light", "dark", or "system"
    font_size: str = "Medium"  # "Small", "Medium", or "Large"
    font_family: str = "Arial"  # Font family name
