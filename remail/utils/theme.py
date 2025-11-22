import flet as ft


def get_current_theme(page):
    theme_mode_map = _get_theme_mode_map()

    return theme_mode_map.get(page.theme_mode, "system")


def _get_theme_mode_map():
    return {
        ft.ThemeMode.LIGHT: "light",
        ft.ThemeMode.DARK: "dark",
        ft.ThemeMode.SYSTEM: "system",
    }