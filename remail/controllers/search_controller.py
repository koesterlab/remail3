import threading
import time
from datetime import datetime

import sqlite_vec
from sqlalchemy import event, text
from sqlmodel import Session, select

from remail.database import engine
from remail.interfaces.embeddings import EmbeddingService
from remail.interfaces.embeddings.text_chunker_service import TextChunkerService
from remail.models import Email


class SearchController:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chunker = TextChunkerService()
        self.engine = engine

        self._register_event_listeners()
        self.init_vector_table()

    def _register_event_listeners(self):
        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_record):
            dbapi_connection.enable_load_extension(True)
            sqlite_vec.load(dbapi_connection)
            dbapi_connection.enable_load_extension(False)

    def init_vector_table(self):
        vector_dim = 768

        create_table_sql = f"""
           CREATE VIRTUAL TABLE IF NOT EXISTS email_chunks USING vec0(
               chunk_id INTEGER PRIMARY KEY,
               +email_id INTEGER,
               +chunk_index INTEGER,
               +content TEXT,
               embedding float[{vector_dim}]
           );
           """

        with self.engine.begin() as conn:
            conn.execute(text(create_table_sql))

    def index_email(self, email_id: int, subject: str, body: str):
        # Check whether chunks already exist for this email
        check_sql = "SELECT COUNT(*) FROM email_chunks WHERE email_id = :email_id"

        with self.engine.begin() as conn:
            result = conn.execute(text(check_sql), {"email_id": email_id})
            if result.fetchone()[0] > 0:
                return

        chunks = self.chunker.chunk_text(body)

        # Fallback: Use the subject if the body is empty
        if not chunks and subject:
            chunks = [subject]

        with self.engine.begin() as conn:
            for index, chunk_text in enumerate(chunks):
                enriched_content = f"Betreff: {subject}\n\n{chunk_text}"

                vector = self.embedding_service.get_embedding(enriched_content)
                vector_blob = sqlite_vec.serialize_float32(vector)

                insert_sql = """
                             INSERT INTO email_chunks(email_id, chunk_index, content, embedding)
                             VALUES (:email_id, :chunk_index, :content, :embedding) \
                             """

                conn.execute(
                    text(insert_sql),
                    {
                        "email_id": email_id,
                        "chunk_index": index,
                        "content": enriched_content,
                        "embedding": vector_blob,
                    },
                )

    def search(self, query: str):
        if query == "":
            return []

        query_vector = self.embedding_service.get_embedding(query)
        query_blob = sqlite_vec.serialize_float32(query_vector)

        search_sql = """
                     SELECT email_id, distance
                     FROM email_chunks
                     WHERE embedding MATCH :query_embedding
                     ORDER BY distance LIMIT 20 \
                     """

        with self.engine.begin() as conn:
            result = conn.execute(text(search_sql), {"query_embedding": query_blob})
            rows = result.fetchall()

        seen_email_ids = set()
        unique_email_ids = []

        for row in rows:
            email_id = row[0]
            if email_id not in seen_email_ids:
                seen_email_ids.add(email_id)
                unique_email_ids.append(email_id)

            if len(unique_email_ids) == 10:
                break

        return unique_email_ids

    def get_embedding_count(self) -> int:
        count_sql = "SELECT COUNT(*) FROM email_chunks"
        with self.engine.begin() as conn:
            result = conn.execute(text(count_sql))
            return int(result.fetchone()[0])

    def index_existing_emails(self):
        email_data_to_process = []
        with Session(self.engine) as session:
            emails = session.exec(select(Email)).all()

            for email in emails:
                if email.id is None:
                    continue

                subject = email.thread.title if email.thread else ""
                body = email.body or ""
                email_data_to_process.append((email.id, subject, body))

        for email_id, subject, body in email_data_to_process:
            try:
                self.index_email(
                    email_id=email_id,
                    subject=subject,
                    body=body,
                )
                # A tiny buffer (50 milliseconds) so the IMAP sync
                # in the main thread can occasionally write to the database.
                time.sleep(0.05)

            except sqlite_vec.OperationalError:
                continue
            except Exception as e:
                print(f"Fehler bei Email {email_id}: {e}")

        print(
            f"[{datetime.now().strftime('%H:%M:%S.%f')}] [Thread: {threading.current_thread().name}] -> Embeddings finished!"
        )
