"""Settings view for local Ollama models."""

import flet as ft

from remail.interfaces.llm import OllamaService


class LocalModelsView(ft.Container):
    def __init__(self):
        super().__init__()

        self.ollama_service = OllamaService()

        self.status_text = ft.Text()
        self.models_dropdown = ft.Dropdown(
            label="Installed local models",
            options=[],
            width=400,
        )

        self.content = ft.Column(
            controls=[
                ft.Text(
                    "Local Models",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Manage local Ollama models that can be used by the app.",
                ),
                self.status_text,
                self.models_dropdown,
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Text("Refresh models"),
                            on_click=self.refresh_models,
                        ),
                    ],
                ),
            ],
            spacing=16,
        )

        self.refresh_models(update=False)

    def refresh_models(self, e=None, update: bool = True):
        try:
            models = self.ollama_service.list_models()
        except Exception:
            self.status_text.value = (
                "Ollama is not running. Please start Ollama and try again."
            )
            self.models_dropdown.options = []
            self.models_dropdown.value = None

            if update:
                self.update()

            return

        self.models_dropdown.options = [
            ft.dropdown.Option(model.name)
            for model in models
        ]

        if models:
            self.models_dropdown.value = models[0].name
            self.status_text.value = f"Found {len(models)} local model(s)."
        else:
            self.models_dropdown.value = None
            self.status_text.value = "Ollama is running, but no local models were found."

        if update:
            self.update()
