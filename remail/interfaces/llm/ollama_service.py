"""Service for communicating with a local Ollama server."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


def _validate_base_url(base_url: str) -> str:
    """Validate and normalize the Ollama base URL."""
    parsed_url = urlparse(base_url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Ollama base URL must use http or https.")

    if not parsed_url.netloc:
        raise ValueError("Ollama base URL must include a host.")

    return base_url.rstrip("/")


@dataclass(frozen=True)
class OllamaModel:
    """Represents a locally installed Ollama model."""

    name: str
    size: int | None = None
    modified_at: str | None = None


class OllamaService:
    """Small wrapper around the local Ollama REST API."""

    def __init__(self, base_url: str = DEFAULT_OLLAMA_BASE_URL):
        self.base_url = _validate_base_url(base_url)

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

        with urlopen(request, timeout=3) as response:  # nosec B310
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

    def pull_model(self, model_name: str) -> Iterator[dict]:
        """Download a model through the local Ollama server."""
        payload = json.dumps({"model": model_name}).encode("utf-8")

        request = Request(
            url=f"{self.base_url}/api/pull",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=None) as response:  # nosec B310
            for line in response:
                if not line:
                    continue

                decoded_line = line.decode("utf-8").strip()

                if not decoded_line:
                    continue

                yield json.loads(decoded_line)

    def generate_response(self, model_name: str, prompt: str) -> str:
        """Generate a response with a local Ollama model."""
        payload = json.dumps(
            {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            },
        ).encode("utf-8")

        request = Request(
            url=f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=None) as response:  # nosec B310
            response_body = response.read().decode("utf-8")

        data: dict[str, Any] = json.loads(response_body)
        response_text = data.get("response", "")

        if isinstance(response_text, str):
            return response_text

        return str(response_text)
