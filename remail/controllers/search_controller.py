import sqlite_vec

from sqlalchemy import event
from sqlalchemy import text
from sqlmodel import Session, select

from remail.database import engine
from remail.interfaces.embeddings import EmbeddingService
from remail.models import Email


class SearchController:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.engine = engine

        # Register event to activate the vector extension
        self._register_event_listeners()
        self.init_vector_table()


    def _register_event_listeners(self):
        # Register event listener for database connection

        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_record):
            # Activate vector extension
            dbapi_connection.enable_load_extension(True)

            sqlite_vec.load(dbapi_connection)
            # Close the extension
            dbapi_connection.enable_load_extension(False)


    def init_vector_table(self):
        # Create the vector table if it doesn't exist

        vector_dim = 768

        create_table_sql = f"""
           CREATE VIRTUAL TABLE IF NOT EXISTS email_embeddings USING vec0(
               email_id INTEGER PRIMARY KEY,
               embedding float[{vector_dim}]
           );
           """

        with self.engine.begin() as conn:
            conn.execute(text(create_table_sql))


    def index_email(self, email_id: int, subject: str, body: str):
        # make one text from subject and body
        full_text = subject + " " + body
        safe_text = full_text[:10000]

        # make a vector from the text
        vector = self.embedding_service.get_embedding(safe_text)
        vector_blob = sqlite_vec.serialize_float32(vector)

        # delete old embedding if exists
        delete_sql = "DELETE FROM email_embeddings WHERE email_id = :email_id"

        # save the new vector in the database
        insert_sql = """
                     INSERT INTO email_embeddings(email_id, embedding)
                     VALUES (:email_id, :embedding)
                     """

        with self.engine.begin() as conn:
            conn.execute(text(delete_sql), {"email_id": email_id})
            conn.execute(text(insert_sql), {"email_id": email_id, "embedding": vector_blob})


    def search(self, query: str):
        # if query is empty, return nothing
        if query == "":
            return []

        # make a vector from the search query
        query_vector = self.embedding_service.get_embedding(query)
        query_blob = sqlite_vec.serialize_float32(query_vector)

        count_sql = "SELECT COUNT(*) FROM email_embeddings"

        # find the 10 most similar emails
        search_sql = """
                     SELECT email_id, distance
                     FROM email_embeddings
                     WHERE embedding MATCH :query_embedding
                     ORDER BY distance
                     LIMIT 10
                     """

        with self.engine.begin() as conn:
            result = conn.execute(text(search_sql), {"query_embedding": query_blob})
            rows = result.fetchall()

        # put the email ids in a list
        email_ids = []
        for row in rows:
            print("Search result:", row[0], "distance:", row[1])
            email_ids.append(row[0])

        return email_ids

    def index_existing_emails(self):
        with Session(self.engine) as session:
            emails = session.exec(select(Email)).all()

            print("Indexing existing emails:", len(emails))

            for email in emails:
                if email.id is None:
                    continue

                subject = email.thread.title if email.thread else ""
                body = email.body or ""

                print("Total emails:", len(emails))
                print("Indexing email:", email.id)

                self.index_email(
                    email_id=email.id,
                    subject=subject,
                    body=body,
                )