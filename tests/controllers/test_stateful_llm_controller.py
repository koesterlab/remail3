import pytest
from remail.controllers.stateful_llm_controller import StatefulLlmController

@pytest.fixture
async def test():
    models = [
        "o1", "o1-2024-12-17", "o1-pro", "o1-pro-2025-03-19", "o1-preview", "o1-preview-2024-09-12",
        "o1-mini", "o1-mini-2024-09-12", "o3-mini", "o3-mini-2025-01-31", "o3", "o3-2025-04-16",
        "o3-pro", "o3-pro-2025-06-10", "o4-mini", "o4-mini-2025-04-16", "gpt-5", "gpt-5-2025-08-07",
        "gpt-5-mini", "gpt-5-mini-2025-08-07", "gpt-5-nano", "gpt-5-nano-2025-08-07", "gpt-5-pro",
        "gpt-5-pro-2025-10-06", "gpt-5.1", "gpt-5.1-2025-11-13", "gpt-4", "gpt-4-32k", "gpt-4-1106-preview",
        "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-vision-preview", "gpt-4-1106-vision-preview",
        "gpt-4-turbo-2024-04-09", "gpt-4-turbo", "gpt-4o", "gpt-4o-audio-preview", "gpt-4o-audio-preview-2024-12-17",
        "gpt-4o-audio-preview-2024-10-01", "gpt-4o-mini-audio-preview", "gpt-4o-mini-audio-preview-2024-12-17",
        "gpt-4o-2024-05-13", "gpt-4o-2024-08-06", "gpt-4o-2024-11-20", "gpt-4.5-preview", "gpt-4.5-preview-2025-02-27",
        "chatgpt-4o-latest", "gpt-4o-mini", "gpt-4o-mini-2024-07-18", "gpt-4-0613", "gpt-4-32k-0613",
        "gpt-4-0314", "gpt-4-32k-0314", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.1-2025-04-14",
        "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-5-chat-latest", "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0301", "text-davinci-003", "text-davinci-002",
        "gpt-3.5-turbo-instruct", "text-ada-001", "text-babbage-001", "text-curie-001", "ada",
        "babbage", "curie", "davinci", "gpt-35-turbo-16k", "gpt-35-turbo", "gpt-35-turbo-0125",
        "gpt-35-turbo-1106", "gpt-35-turbo-0613", "gpt-35-turbo-16k-0613"
    ]
    for model in models:
        print("Testing", model)
        llm = StatefulLlmController(model, temperature=0.2, max_tokens=1024)

        def getCurrentDraft() -> str:
            print("Called: getCurrentDraft")
            return ""

        llm.add_tool("getCurrentDraft",
                     "Returns the text in the current write-email dialog. \"\" if no email is written",
                     getCurrentDraft)
        llm.build_agent("Hallo Welt")
        try:
            response = await llm.query("Hallo, das ist ein Test")
            print("-- Funktioniert: ", response)
        except Exception as e:
            print("Fehler: ", e)
            pass
