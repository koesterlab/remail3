"""LLM interface module."""

from .base import LLMBase
from .llm_service import LLMService
from .ollama_service import OllamaModel, OllamaService

__all__ = ["LLMBase", "LLMService", "OllamaModel", "OllamaService"]
