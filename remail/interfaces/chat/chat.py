from llama_index.llms.ollama import Ollama


class ChatService:
    def __init__(self):
        self.llm = Ollama(model="llama3.2", request_timeout=120.0)

    def get_response(self, message: str) -> str:
        response = self.llm.complete(message)
        return str(response)