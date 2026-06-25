import re
from llama_index.core.node_parser import SentenceSplitter

class TextChunkerService:
    """Service zum Bereinigen und Zerschneiden von Texten für Embeddings."""
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self._chunker = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap)

    def clean_email_text(self, text: str) -> str:
        """Bereinigt E-Mails (Zitate, HTML, Formatierung) für optimale Embeddings."""
        if not text:
            return ""

        # 1. Zitierte Antworten entfernen (> oder >> am Zeilenanfang)
        clean_text = re.sub(r'(?m)^\s*>.*$', '', text)

        # 2. HTML-Tags entfernen (mit Leerzeichen ersetzen, damit Wörter nicht zusammenkleben!)
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)

        # 3. Normale Leerzeichen und Tabs bereinigen (Zeilenumbrüche bleiben verschont)
        clean_text = re.sub(r'[ \t]+', ' ', clean_text)

        # 4. Übertriebene Zeilenumbrüche reduzieren (Absätze \n\n bleiben erhalten)
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)

        return clean_text.strip()

    def chunk_text(self, text: str) -> list[str]:
        """Bereinigt den Text und teilt ihn in überlappende Chunks auf."""
        cleaned_text = self.clean_email_text(text)

        if not cleaned_text:
            return []

        return self._chunker.split_text(cleaned_text)