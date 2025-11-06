import os
import sys

# Add the Remail directory (parent folder) to sys.path
remail_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(remail_path)

import controller  # noqa: E402

# import RAG_Backend

emails = controller.controller.get_emails()
print(emails)

# llm= RAG_Backend.LLM()
# llm._connectToDb()
