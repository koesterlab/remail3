import flet as ft

popular_timezones = [
    "America/New_York (UTC-05:00)",
    "America/Chicago (UTC-06:00)",
    "America/Los_Angeles (UTC-08:00)",
    "Europe/London (UTC+00:00)",
    "Europe/Berlin (UTC+01:00)",
    "Europe/Moscow (UTC+03:00)",
    "Asia/Dubai (UTC+04:00)",
    "Asia/Shanghai (UTC+08:00)",
    "Asia/Tokyo (UTC+09:00)",
    "Australia/Sydney (UTC+11:00)",
    "Pacific/Auckland (UTC+13:00)",
]
all_languages = [
    "English",
    "German",
    "Russian",
    "Spanish",
    "French",
    "Italian",
    "Portuguese",
    "Dutch",
    "Polish",
    "Czech",
    "Japanese",
    "Chinese",
    "Korean",
    "Arabic",
    "Hindi",
    "Turkish",
    "Swedish",
    "Norwegian",
    "Danish",
    "Finnish",
]


def create_language_setting():
    return ft.Container(
        ft.Column(
            [
                ft.Text("Language & Region", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Choose your prefferred language for the application"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
                ft.Text("Application Language"),
                ft.Dropdown(
                    value="German",
                    options=[ft.dropdown.Option(lang) for lang in all_languages],
                    menu_height=200,
                    expand=True,
                ),
                ft.Text("Timezone"),
                ft.Dropdown(
                    value="Europe/Berlin (UTC+01:00)",
                    options=[ft.dropdown.Option(tz) for tz in popular_timezones],
                    menu_height=200,
                    expand=True,
                ),
                ft.Container(ft.OutlinedButton("Apply"), alignment=ft.alignment.center),
            ]
        ),
        # bgcolor=ft.Colors.GREY_100,
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
