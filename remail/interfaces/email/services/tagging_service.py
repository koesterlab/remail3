"""Email tagging service using LLM-based multi-label classification."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, create_model

from remail.interfaces.llm.localLLMService import LocalLLM


class TaggingService:
    """
    manages tags db and llm interaction

    Responsibilities:
    - Build the classification prompt.
    - Delegate to Ollama for structured LLM inference

    """
    _BODY_CHAR_LIMIT = 1500

    def __init__(self, llm: LocalLLM) -> None:
        self._llm = llm

    def _build_result_schema(self, tags: dict[str, str]) -> type[BaseModel]:
        TagLiteral = Literal[tuple(tags.keys())] #for json enums 
        return create_model("EmailTagResult", tags=(list[TagLiteral], ...),
        )

    def _infer_tag_with_llm(
        self,
        body: str,
        tags: dict[str, str],
        max_tags: int = 3,
    ) -> BaseModel:
        """
        Classify an email by assigning 1 to `max_tags` tags from `tags`.

        Args:
            body: Email body text (truncated internally to avoid token overuse).
            tags: Mapping of tag name -> description, e.g.
                  {"Work": "Professional emails, meetings, ...", ...}
            max_tags: Soft upper bound on the number of tags assigned.
                      Enforced via the prompt, not the schema.

        Returns:
            Validated Pydantic instance with:
              - `tags`: list of assigned tag names (each a valid key from `tags`)

        Raises:
            ValueError: If `tags` is empty.
            RuntimeError: If the underlying LLM call fails.
        """
        if not tags:
            raise ValueError("tags dict must not be empty.")

        tag_descriptions = "\n".join(
            f'- "{name}": {description}' for name, description in tags.items()
        )
        system_prompt = (
            f"You are an email classifier. Assign between 1 and {max_tags} tags that clearly apply to the email.\n\n"
            f"Available tags:\n{tag_descriptions}\n\n"
            "Rules:\n"
            "- Only use tags from the list above.\n"
            "- Only assign a tag if it clearly applies — do not over-tag.\n"
            "- Always assign at least one tag.\n"
        )

        user_prompt = (
            f"{body[: self._BODY_CHAR_LIMIT]}"
        )

        return self._llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=self._build_result_schema(tags),
            temperature=0.0,
        )

    def get_tags_for_email(self, body: str, tags: dict[str, str]) -> list[str]:
        """
        Get tags for an email body.

        Args:
            body: Email body text.
            tags: Mapping of tag name -> description, e.g.
                  {"Work": "Professional emails, meetings, ...", ...}

        Returns:
            List of assigned tag names (each a valid key from `tags`)

        Raises:
            ValueError: If `tags` is empty.
            RuntimeError: If the underlying LLM call fails.
        """
        result = self._infer_tag_with_llm(body=body, tags=tags)
        return result.tags
