import sqlite_vec
from remail.database import engine
from remail.interfaces.embeddings import EmbeddingService
from sqlalchemy import event
from sqlalchemy import text

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

    def index_email(self, email_id: int, text: str):
        vector = self.embedding_service.get_embedding(text)

        # Insert the list in a Binary Package
        vector_blob = sqlite_vec.serialize_float32(vector)
        insert_sql = """
                     INSERT INTO email_embeddings(email_id, embedding)
                     VALUES (:email_id, :embedding)
                     """

        with self.engine.begin() as conn:
            conn.execute(text(insert_sql), {"email_id": email_id, "embedding": vector_blob})
