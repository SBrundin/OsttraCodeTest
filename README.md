# OSTTRA Messaging Application

This is a simple messaging service that allows you to send, retrieve, and delete text messages using a REST API.

## Features:
1. **Send Message:** Send a message to a recipient identified by username.
2. **Get New Messages:** Retrieve new messages since the last retrieval.
3. **Delete Messages:** Delete one or more messages for a recipient.
4. **Get Messages by Range:** Retrieve a list of messages in time order based on a start and stop index.

## Setup

### Prerequisites
- Python 3.7 or above
- `pip` package manager

### Installation
1. Clone the repository from https://github.com/SBrundin/OsttraCodeTest or open the attached zip-file.
2. Navigate to the project directory.
3. Install the required packages: 
```bash
pip install -r requirements.txt
```

**Start the application**: 
```bash
python app.py
```

The app will start on http://localhost:5000 by default.

## Interact with the API
Open a separate terminal and use curl to interact with the API. See section below for details about how to use it.

## API Endpoints
### 1. Send a Message
- **Endpoint:** `POST /send_message`
- **Example:**

```bash
curl -X POST http://localhost:5000/send_message \
-H "Content-Type: application/json" \
-d '{"sender": "Foo", "recipient": "Bar", "message": "Hello, Bar!"}'
```

Response:
```json
{
  "status": "Message sent",
  "message_id": "abcd-1234-efgh-5678"
}
```

### 2. Get Messages for a Recipient

- **Endpoint:** `GET /get_messages/<recipient>'`
- **Query Params:** last_retrieved (optional)
- **Example:**
```bash
curl -X GET http://localhost:5000/get_messages/Bar
```
or with query parameter:
```bash
curl -X GET http://localhost:5000/get_messages/Bar?last_retrieved=2024-09-07
```
Response:
```json
{
  "messages": [
    {
      "id": "abcd-1234-efgh-5678",
      "sender": "Foo",
      "message": "Hello, Bar!",
      "timestamp": "2024-09-08T12:34:56"
    }
  ]
}
```


### 3. Delete Messages for a Recipient
- **Endpoint:** `DELETE /delete_messages/<recipient>'`
- **Example:**
```bash
curl -X DELETE http://localhost:5000/delete_messages/Bar \
-H "Content-Type: application/json" \
-d '{"message_ids": ["abcd-1234-efgh-5678"]}'
```
Response:
```json
{
  "status": "Deleted 1 messages"
}
```

### 4. Retrieve Time-Ordered Messages for a Recipient Based on Start and Stop Index.
- **Endpoint:** `GET /get_messages_range/<recipient>'`
- **Example:**
```bash
curl -X GET "http://localhost:5000/get_messages_range/Bar?start=0&stop=5"
```
Response:
```json
{
  "messages": [
    {
      "id": "abcd-1234-efgh-5678",
      "sender": "Foo",
      "message": "Hello, Bar!",
      "timestamp": "2024-09-08T12:34:56"
    }
  ]
}
```

## Testing
This project includes unit tests for the API.

To run the tests, execute:
```bash
pytest test_app.py
```