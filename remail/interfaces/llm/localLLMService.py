"""local Ollama-backed LLM service with structured output support."""

from __future__ import annotations


import atexit

import shutil

import subprocess
import time

from typing import Any, Literal


from ollama import chat, list as ollama_list, pull as ollama_pull

from pydantic import BaseModel, create_model


class LocalLLM:
    """
    to refactor later. testes only on a machine with ollama installed and running
    LLM service backed by a local Ollama instance.

    On construction (with ``auto_start=True``) the service will start a local

    ``ollama serve`` process if one is not already running, and pull the
    requested model if it is not already installed.
    """

    _server_process: subprocess.Popen | None = None


    def __init__(self, model: str = "llama3.2:1b", auto_start: bool = True) -> None:  # the smallest model
        """
        Args:
            model: Ollama model name to use for completions.
            auto_start: If True, ensure the Ollama server is running and the
            model is available before returning.
        """

        self.model = model

        if auto_start:
            self._ensure_server_running()
            self._ensure_model_available()


    @staticmethod

    def _installed_models() -> list[str] | None:
        """Return installed model names, or None if the server is unreachable."""
        try:
            return [m.model or "" for m in ollama_list().models]
        except Exception:
            return None


    @classmethod
    def _ensure_server_running(cls, timeout: float = 30.0) -> None:
        """
        Start a local Ollama server if one is not already running.
        Only the process started here is tracked for shutdown; a pre-existing
        server is left untouched.

        Raises:
            RuntimeError: If Ollama is not installed or the server does not
                become ready within ``timeout`` seconds.
        """

        if cls._installed_models() is not None:
            return

        if shutil.which("ollama") is None:
            raise RuntimeError(
                "Ollama is not installed or not on PATH. Install from https://ollama.com"
            )

        cls._server_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        atexit.register(cls._stop_server)

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if cls._installed_models() is not None:
                return
            time.sleep(0.5)

        raise RuntimeError(f"Ollama server did not become ready within {timeout}s")


    @classmethod

    def _stop_server(cls) -> None:

        """Terminate the server process started by this class, if any."""

        if cls._server_process is not None:

            cls._server_process.terminate()

            try:

                cls._server_process.wait(timeout=5)

            except subprocess.TimeoutExpired:

                cls._server_process.kill()

            cls._server_process = None


    def _ensure_model_available(self) -> None:
        """

        Pull ``self.model`` if it is not already installed.


        Progress is printed in place. Requires the server to be running.


        Raises:

            RuntimeError: If the pull fails.
        """

        installed = self._installed_models() or []

        wanted = {self.model, self.model.split(":")[0]}

        if any(n in wanted or n.split(":")[0] in wanted for n in installed):
            return


        print(f"Model '{self.model}' not found locally. Pulling...")

        try:

            last_pct = -1

            for progress in ollama_pull(self.model, stream=True):

                total = getattr(progress, "total", None)

                completed = getattr(progress, "completed", None)

                if total and completed:

                    pct = int(completed / total * 100)

                    if pct != last_pct:

                        print(f"\r  {progress.status}: {pct}%", end="", flush=True)

                        last_pct = pct

                elif progress.status:

                    print(f"\r  {progress.status}", end="", flush=True)

            print()  # newline after progress

        except Exception as e:

            raise RuntimeError(f"Failed to pull model '{self.model}': {e}") from e


    def generate_structured(

        self,

        system_prompt: str,

        user_prompt: str,

        schema: type[BaseModel],

        temperature: float = 0.0,

        **kwargs: Any,

    ) -> BaseModel:
        """

        Generate a response constrained to a Pydantic schema.


        Args:

            system_prompt: Instruction context for the model.

            user_prompt: The user message / content to classify or process.

            schema: Pydantic model class whose schema constrains the output.

            temperature: Sampling temperature. Use 0.0 for deterministic output.

            **kwargs: Additional options forwarded to Ollama (e.g. num_ctx).


        Returns:

            A validated instance of `schema`.


        Raises:

            RuntimeError: If the Ollama call fails or validation fails.
        """

        try:

            response = chat(

                model=self.model,

                messages=[

                    {"role": "system", "content": system_prompt},

                    {"role": "user", "content": user_prompt},

                ],

                format=schema.model_json_schema(),

                options={"temperature": temperature, **kwargs},

            )

            content = response.message.content

            if content is None:

                raise RuntimeError("Ollama response content is missing")

            return schema.model_validate_json(content)


        except Exception as e:

            raise RuntimeError(f"Ollama structured completion failed: {e}") from e
        



# for testing my sanity and prompt design, not used by the app

if __name__ == "__main__":

    def _build_result_schema(tags: dict[str, str]) -> type[BaseModel]:

        TagLiteral = Literal[tuple(tags.keys())] #for json enums 

        return create_model("EmailTagResult", tags=(list[TagLiteral], ...),

        )
    

    tags = {"Work": "Professional emails, meetings, ...", 
            "Personal": "Friends, family, ...",
            "Urgent": "Requires immediate attention"}

    tag_descriptions = "\n".join(
        f'- "{name}": {description}' for name, description in tags.items())

    system_prompt = (
        f"You are an email classifier. Assign between 1 and 3 tags that clearly apply to the email.\n\n"
        f"Available tags:\n{tag_descriptions}\n\n"
        "Rules:\n"
        "- Only use tags from the list above.\n"
        "- Only assign a tag if it clearly applies — do not over-tag.\n"
        "- Always assign at least one tag.\n"
    )


    svc = LocalLLM()

    result = svc.generate_structured(
        system_prompt=system_prompt,
        user_prompt="Subject: Meeting tomorrow\nHi, just a reminder about our 10am standup. Please bring the Q2 report.",
        schema=_build_result_schema(tags),

    )

    print(result)