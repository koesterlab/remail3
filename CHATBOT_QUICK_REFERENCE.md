# Quick Reference: AI Chatbot Implementation

## Architecture Overview

```
AppState.active_thread (user selects a thread)
    ↓
Chatbot UI (create_chatbot_view)
    ↓
LLMController.chat_with_thread_context()
    ├─ ChatService.get_or_create_session()
    ├─ ChatService.build_thread_context()
    ├─ ChatService.save_message() [user]
    ├─ LLMService.generate_completion()
    ├─ ChatService.save_message() [assistant]
    └─ Database (ChatSession, ChatMessage)
```

## Core Components

### 1. Database Models

**ChatSession**
- Stores conversations for each user+thread combination
- Fields: id, user_id, thread_id, created_at, updated_at
- Relationships: User (many-to-one), ChatMessages (one-to-many)

**ChatMessage**
- Individual messages in a conversation
- Fields: id, session_id, role ("user"/"assistant"), content, created_at
- Relationship: ChatSession (many-to-one)

### 2. ChatService (remail/interfaces/llm/services/chat_service.py)

```python
service = ChatService(db_session)

# Get or create session
session = service.get_or_create_session(user_id=1, thread_id=123)

# Build context from thread emails
context = service.build_thread_context(thread_id=123)

# Save messages
msg = service.save_message(session_id=session.id, role="user", content="Hi")

# Retrieve conversation history
messages = service.get_session_messages(session_id=session.id)
```

### 3. LLMController Enhancement (remail/controllers/llm_controller.py)

```python
# Initialize with database session
controller = LLMController(db_session=session)

# Chat with thread context
result = controller.chat_with_thread_context(
    user_id=1,
    thread_id=123,
    user_message="What about this?",
    system_prompt="You are an email assistant",  # optional
    max_tokens=500,  # optional
    temperature=0.7  # optional
)

if result["status"] == "success":
    print(result["completion"])  # Assistant response
    session_id = result["session_id"]  # Session ID for future reference
```

### 4. Chatbot UI (remail/client/views/chatbot.py)

```python
# In a Flet application
def main(page: ft.Page):
    app_state = AppState()
    chatbot_view = create_chatbot_view(page, app_state)
    page.add(chatbot_view)
```

**Features:**
- Shows thread ID in header
- Displays "Select a thread to chat about it" when no thread selected
- Loads previous messages when thread changes
- Auto-scrolling message list
- User/Assistant message styling
- Error notifications

## State Flow

### Selecting a Thread
```
user clicks thread
  ↓
AppState.active_thread = thread_id
  ↓
Chatbot UI updates header with thread info
  ↓
load_chat_history() fetches previous messages from ChatService
  ↓
Messages displayed in message_display Column
```

### Sending a Message
```
user types and clicks send
  ↓
validate app_state.active_thread exists
  ↓
display user message in UI
  ↓
call LLMController.chat_with_thread_context()
  ├─ ChatService gets/creates session
  ├─ ChatService builds thread context
  ├─ ChatService saves user message
  ├─ LLMService generates response
  ├─ ChatService saves assistant response
  └─ returns result with completion
  ↓
display assistant response in UI
```

## Database Queries

### Find all sessions for a user
```python
from sqlmodel import Session, select
from remail.models import ChatSession

stmt = select(ChatSession).where(ChatSession.user_id == user_id)
sessions = db_session.exec(stmt).all()
```

### Get conversation history
```python
from sqlmodel import Session, select
from remail.models import ChatMessage

stmt = select(ChatMessage).where(
    ChatMessage.session_id == session_id
).order_by(ChatMessage.created_at)
messages = db_session.exec(stmt).all()
```

### Clear chat history for a session
```python
session_to_delete = db_session.get(ChatSession, session_id)
db_session.delete(session_to_delete)
db_session.commit()
```

## Testing

### Unit Tests (ChatService)
```bash
pytest tests/interfaces/llm/test_chat_service.py -v
```
Tests session creation, message persistence, thread context building, etc.

### Integration Tests (LLMController)
```bash
pytest tests/controllers/test_llm_controller_chat.py -v
```
Tests end-to-end chat flow with mocked LLM service

### Run All Chat Tests
```bash
pytest tests/interfaces/llm/test_chat_service.py tests/controllers/test_llm_controller_chat.py -v
```

## Configuration

### Environment Variables (needed for actual LLM calls)
```bash
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://your-llm-endpoint/v1
```

### AppState Integration
```python
from remail.client.state.app_state import AppState

app_state = AppState()

# Set active thread when user selects one
app_state.active_thread = 123

# Check if thread is selected
if app_state.active_thread:
    print(f"Chatting about thread {app_state.active_thread}")
else:
    print("No thread selected")
```

## Troubleshooting

### "Chat service not available" error
- Ensure LLMController was initialized with a db_session
- Check: `controller = LLMController(db_session=your_session)`

### No active thread message in chatbot
- Check AppState: `print(app_state.active_thread)`
- Set it: `app_state.active_thread = thread_id`

### Messages not persisting
- Ensure SQLModel tables are created in database
- Check ChatSession and ChatMessage tables exist
- Verify db_session is properly committed

### LLM API errors
- Check environment variables are set
- Verify API endpoint and key are correct
- Check network connectivity to LLM service

## Performance Considerations

1. **Thread Context Size**: Limit email threads to reasonable size to avoid token overflow
2. **Message History**: Consider pagination for very long conversations (1000+ messages)
3. **Database Indexes**: Add indexes on (user_id, thread_id) for faster session lookups
4. **Caching**: Consider caching thread context for frequently discussed threads

## Security Considerations

1. **Authentication**: Ensure only authenticated users can create chat sessions
2. **Authorization**: Users should only see/modify their own chat sessions
3. **Input Validation**: Validate user messages for injection attacks
4. **Data Privacy**: Consider encryption for sensitive email content in prompts

## API Reference

### LLMController.chat_with_thread_context()

**Parameters:**
- `user_id` (int): ID of user sending message
- `thread_id` (int): ID of email thread for context
- `user_message` (str): User's message
- `system_prompt` (str, optional): Custom system prompt
- `max_tokens` (int, optional): Max response length
- `temperature` (float, optional): LLM temperature (0.0-2.0)

**Returns:**
```python
{
    "status": "success" | "error",
    "message": "...",
    "session_id": int,  # if success
    "completion": "...",  # if success
    "response": LLMCompletionResponse  # if success
}
```

### ChatService Methods

- `get_or_create_session(user_id: int, thread_id: int) → ChatSession`
- `build_thread_context(thread_id: int) → str`
- `save_message(session_id: int, role: str, content: str) → ChatMessage`
- `get_session_messages(session_id: int) → list[ChatMessage]`
- `update_session_timestamp(session_id: int) → None`
