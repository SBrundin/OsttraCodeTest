import pytest
from app import app
import json
from unittest.mock import patch, mock_open
from datetime import datetime

mock_message = {
    "Foo": [
        {
            "id": "abcd-1234-efgh-5678",
            "sender": "Bar",
            "message": "Hello World!",
            "timestamp": "2024-09-08T12:34:56"
        }
    ]
}

multiple_unsorted_mock_messages = {
    "Foo": [
        {
            "id": "2",
            "sender": "Bar",
            "message": "I got sent second.",
            "timestamp": "2024-09-08T12:34:56"
        },

        {
            "id": "1",
            "sender": "Bar",
            "message": "I was sent first.",
            "timestamp": "2024-09-05T11:34:56"
        },

        {
            "id": "3",
            "sender": "FooBar",
            "message": "I am the latest message!",
            "timestamp": "2024-09-10T13:34:56"
        }
    ]
}


def mock_open_messages():
    return mock_open(read_data=json.dumps(mock_message))


def mock_open_multiple_unsorted_messages():
    return mock_open(read_data=json.dumps(multiple_unsorted_mock_messages))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_send_message(client):
    with patch("builtins.open", mock_open_messages()):
        response = client.post('/send_message', json={
            "sender": "Bar",
            "recipient": "Foo",
            "message": "My first message"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert data["status"] == "Message sent"


def test_fail_to_send_message(client):
    with patch("builtins.open", mock_open_messages()):
        response = client.post('/send_message', json={
            "sender": "Bar",
            "message": "I'm missing a recipient"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Missing sender, recipient, or message'
        assert "status" not in data


def test_get_messages(client):
    with patch("builtins.open", mock_open_messages()):
        response = client.get('/get_messages/Foo')
        assert response.status_code == 200
        data = response.get_json()
        assert "messages" in data
        assert len(data["messages"]) == 1
        assert data["messages"][0]["message"] == "Hello World!"


def test_get_new_messages_with_last_retrieved(client):
    with patch("builtins.open", mock_open_multiple_unsorted_messages()):
        # Timestamp chosen to be in between the first message and the later two.
        timestamp = datetime(2024, 9, 6, 11, 30).isoformat()
        response = client.get(f'/get_messages/Foo?last_retrieved={timestamp}')
        assert response.status_code == 200
        data = response.get_json()
        assert "messages" in data
        assert len(data["messages"]) == 2
        assert data["messages"][0]["message"] == "I got sent second."
        assert data["messages"][1]["message"] == "I am the latest message!"


def test_fail_to_get_messages(client):
    with patch("builtins.open", mock_open_messages()):
        response = client.get('/get_messages/UnknownRecipient')
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == "No messages found for recipient: UnknownRecipient"
        assert "messages" not in data


def test_delete_messages(client):
    with patch("builtins.open", mock_open_messages()), patch("app.save_messages"):
        response = client.delete('/delete_messages/Foo', json={
            "message_ids": ["abcd-1234-efgh-5678"]
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert data["status"] == "Deleted 1 messages"


def test_fail_to_delete_messages(client):
    with patch("builtins.open", mock_open_messages()), patch("app.save_messages"):
        response = client.delete('/delete_messages/Foo', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == "No Message IDs Provided"
        assert "messages" not in data


def test_get_messages_range(client):
    with patch("builtins.open", mock_open_messages()):
        response = client.get('/get_messages_range/Foo?start=0&stop=5')
        assert response.status_code == 200
        data = response.get_json()
        assert "messages" in data
        assert len(data["messages"]) == 1
        assert data["messages"][0]["message"] == "Hello World!"


def test_get_messages_range_sorted_in_time(client):
    with patch("builtins.open", mock_open_multiple_unsorted_messages()):
        response = client.get('/get_messages_range/Foo?start=0&stop=2')
        assert response.status_code == 200
        data = response.get_json()
        assert "messages" in data
        assert len(data["messages"]) == 2
        assert data["messages"][0]["message"] == "I was sent first."
        assert data["messages"][1]["message"] == "I got sent second."
