"""Settings view for local Ollama models."""

import flet as ft

from remail.interfaces.llm import OllamaService
from remail.controllers.settings_controller import SettingsController


class LocalModelsView(ft.Container):
    def __init__(self):
        super().__init__()

        self.ollama_service = OllamaService()
        self.settings_controller = SettingsController()
        self.settings = self.settings_controller.get_settings()
        self.ollama_service = OllamaService(self.settings.ollama_base_url)

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
                        ft.ElevatedButton(
                           content=ft.Text("Save selected model"),
                           on_click=self.save_selected_model,
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
            model_names = [model.name for model in models]

            if self.settings.selected_local_model in model_names:
                self.models_dropdown.value = self.settings.selected_local_model
            else:
                self.models_dropdown.value = model_names[0]

            self.status_text.value = f"Found {len(models)} local model(s)."

        else:
            self.models_dropdown.value = None
            self.status_text.value = "Ollama is running, but no local models were found."

        if update:
            self.update()
    def download_model(self, e):
        model_name = self.model_name_input.value.strip()

        if not model_name:
            self.status_text.value = "Please enter a model name first."
            self.update()
            return

        self.status_text.value = f"Downloading model '{model_name}'..."
        self.update()

        try:
            for event in self.ollama_service.pull_model(model_name):
                status = event.get("status", "Downloading model...")

                completed = event.get("completed")
                total = event.get("total")

                if completed and total:
                    percentage = round((completed / total) * 100, 1)
                    self.status_text.value = (
                        f"{status} ({percentage}%)"
                    )
                else:
                    self.status_text.value = status

                self.update()

            self.status_text.value = f"Model '{model_name}' downloaded successfully."
            self.refresh_models(update=False)
            self.update()

        except Exception as exc:
            self.status_text.value = f"Failed to download model: {exc}"
            self.update()


    def save_selected_model(self, e=None):
        selected_model = self.models_dropdown.value

        if not selected_model:
            return

        self.settings.selected_local_model = selected_model
        self.settings_controller.update_settings(self.settings)

        self.status_text.value = f"Selected local model saved: {selected_model}"
        self.update()