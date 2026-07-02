from llama_index.embeddings.ollama import OllamaEmbedding


class EmbeddingService:
    def __init__(self):
        # Initialize the embedding model
        self.embedding_model = OllamaEmbedding(model_name="nomic-embed-text")

    def get_embedding(self, text: str):
        # Get the embedding for the given text
        result = self.embedding_model.get_text_embedding(text)
        return result
