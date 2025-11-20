import flet as ft

from pages.email_accounts import create_connected_email_accounts
from pages.appearance import create_appearance
from pages.notifictatins import create_notifications
from pages.language import create_language_setting
from pages.archived import create_archived


def main(page: ft.Page):
    page.title = "Settings"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    
    settings_content = ft.Container(
        content=ft.Text(""),
        visible=True
        )
    
    
    def email_click(e):
        settings_content.content = create_connected_email_accounts()
        settings_content.update()
    
    def appearance_click(e):
        settings_content.content = create_appearance(page)
        settings_content.update()
    
    def notifications_click(e):
        settings_content.content = create_notifications()
        settings_content.update()
    
    def language_click(e):
        settings_content.content = create_language_setting()
        settings_content.update()
    
    def archived_click(e):
        settings_content.content = create_archived()
        settings_content.update()
    
    buttons = [
        ft.ElevatedButton(
            "Email Accounts",
            icon="mail",
            on_click=email_click
        ),
        ft.ElevatedButton(
            "Appearance",
            icon="palette",
            on_click=appearance_click
        ),
        ft.ElevatedButton(
            "Notifications",
            icon="notifications",
            on_click=notifications_click
        ),
        ft.ElevatedButton(
            "Language",
            icon="language",
            on_click=language_click
        ),
        ft.ElevatedButton(
            "Archived",
            icon="archive",
            on_click=archived_click
        ),
    ]
    
    settings = ft.Container(
        ft.Column(
            [
                ft.Text(
                    "Settings",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text("Manage your account and preferences"),
                ft.Row(
                    buttons,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True, 
                ),
            ],
            spacing=20, 
        ),
        padding=20,
    )
    
    
    page.add(settings,settings_content)
    


ft.app(target=main)