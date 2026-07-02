import re

from llama_index.core.node_parser import SentenceSplitter


class TextChunkerService:
    """Service for cleaning and splitting texts into chunks for embeddings."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self._chunker = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def clean_email_text(self, text: str) -> str:
        """Clean emails by removing quotes, HTML, and formatting for better embeddings."""
        if not text:
            return ""

        # 1. Remove quoted replies (> or >> at the beginning of a line)
        clean_text = re.sub(r"(?m)^\s*>.*$", "", text)

        # 2. Remove HTML tags and replace them with spaces so words do not merge
        clean_text = re.sub(r"<[^>]+>", " ", clean_text)

        # 3. Clean normal spaces and tabs while preserving line breaks
        clean_text = re.sub(r"[ \t]+", " ", clean_text)

        # 4. Reduce excessive line breaks while preserving paragraphs
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)

        return clean_text.strip()

    def chunk_text(self, text: str) -> list[str]:
        cleaned_text = self.clean_email_text(text)

        if not cleaned_text:
            return []

        return self._chunker.split_text(cleaned_text)
