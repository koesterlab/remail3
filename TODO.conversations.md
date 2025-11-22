# TODO


- Conversations List Example:
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

Thread Request:
