## Contacts list request

```json
[
  {
    "contacts": [
      {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "is_known": true,
        "type": "business | personal"
      }
    ],
    "custom_name": "My Contacts List | null",
    "type": "conversation | group",
    "is_favorite": true,
    "threads": [
      {
        "title": "Project Discussion",
        "total_count": 42,
        "unread_count": 5,
        "last_message": "This is a testing message.",
        "last_message_timestamp": "2024-05-30",
        "thread_id": 1
      },
      {
        "title": "Family Reunion",
        "total_count": 42,
        "unread_count": 5,
        "last_message": "This is a testing message.",
        "last_message_timestamp": "2024-05-30",
        "thread_id": 2
      }
    ]
  }
]
```

## Thread request

```json
{
  "id": 1,
  "title": "Project Discussion",
  "messages": [
    {
      "id": 101,
      "sender": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
      },
      "subject": "Meeting Reminder",
      "content": {
        "body": "Hello, how are you?",
        "attachments": [
          {
            "file_name": "agenda.pdf",
            "file_size": 204800,
            "file_type": "application/pdf",
            "url": "https://example.com/attachments/agenda.pdf"
          }
        ]
      },
      "sent_at": "2024-05-30T10:15:30Z"
    },
    {
      "id": 102,
      "sender": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
      },
      "subject": "Re: Meeting Reminder",
      "content": {
        "body": "I'm good, thanks for asking!",
        "attachments": []
      },
      "sent_at": "2024-05-30T10:17:45Z"
    }
  ]
}
```

## Features

- Implement listing the conversations in the main page (In Progress)
- Implement connecting to real email accounts using the email controller (login / logout) (In Progress)
- Implement displaying the thread view (In Code-Review)
- Implement the threads model (In Code-Review)
- Implement controller for fetching the conversations (In Progress)
- 
- Implement fetching the threads/emails
- Implement sending an email and creating/updating a thread
- Implement searching/sorting the conversations
- Implement the settings features and save it locally for the user
- Implement attaching the emails in the AI chatbot and using it to answer questions on the email
- Implement AI actions for the emails (tagging, attaching a priority, ...etc)
- Implement exchange protocol
- Implement Accounts controller for fetching the email.
