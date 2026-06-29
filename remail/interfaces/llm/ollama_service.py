"""Service for communicating with a local Ollama server."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


@dataclass(frozen=True)
class OllamaModel:
    """Represents a locally installed Ollama model."""

    name: str
    size: int | None = None
    modified_at: str | None = None


class OllamaService:
    """Small wrapper around the local Ollama REST API."""

    def __init__(self, base_url: str = DEFAULT_OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def is_available(self) -> bool:
        """Return True if the local Ollama server is reachable."""
        try:
            self.list_models()
            return True
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            return False

    def list_models(self) -> list[OllamaModel]:
        """Return locally installed Ollama models."""
        request = Request(
            url=f"{self.base_url}/api/tags",
            method="GET",
        )

        with urlopen(request, timeout=3) as response:
            response_body = response.read().decode("utf-8")

        data = json.loads(response_body)
        models = data.get("models", [])

        return [
            OllamaModel(
                name=model.get("name", ""),
                size=model.get("size"),
                modified_at=model.get("modified_at"),
            )
            for model in models
            if model.get("name")
        ]