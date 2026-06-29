"""Settings view for local Ollama models."""

import flet as ft


class LocalModelsView(ft.Container):
    def __init__(self):
        super().__init__()

        self.content = ft.Column(
            controls=[
                ft.Text(
                    "Local Models",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Here you will be able to choose and download local Ollama models.",
                ),
            ],
            spacing=16,
        )
        