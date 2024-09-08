from flask import Flask, request, jsonify
import json
import uuid
from datetime import datetime

app = Flask(__name__)

MESSAGE_FILE = 'messages.json'


def load_messages():
    try:
        with open(MESSAGE_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_messages(messages):
    with open(MESSAGE_FILE, 'w') as file:
        json.dump(messages, file, indent=4)


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    if 'sender' not in data or 'recipient' not in data or 'message' not in data:
        return jsonify({"error": "Missing sender, recipient, or message"}), 400

    messages = load_messages()
    message_id = str(uuid.uuid4())
    message_data = {
        "id": message_id,
        "sender": data['sender'],
        "message": data['message'],
        "timestamp": datetime.utcnow().isoformat()
    }

    if data['recipient'] not in messages:
        messages[data['recipient']] = []

    messages[data['recipient']].append(message_data)
    save_messages(messages)

    return jsonify({"status": "Message sent", "message_id": message_id}), 200


@app.route('/get_messages/<recipient>', methods=['GET'])
def get_messages(recipient):
    last_retrieved = request.args.get('last_retrieved', None)
    messages = load_messages()
    recipient_messages = messages.get(recipient, [])
    if not recipient_messages:
        return jsonify({"error": f"No messages found for recipient: {recipient}"}), 400

    if last_retrieved:
        last_time = datetime.fromisoformat(last_retrieved)
        recipient_messages = [msg for msg in recipient_messages if datetime.fromisoformat(
            msg.get('timestamp', [])) > last_time]

    return jsonify({"messages": recipient_messages}), 200


@app.route('/delete_messages/<recipient>', methods=['DELETE'])
def delete_messages(recipient):
    data = request.json
    if 'message_ids' not in data:
        return jsonify({"error": "No Message IDs Provided"}), 400

    messages = load_messages()
    recipient_messages = messages.get(recipient, [])

    new_messages = [msg for msg in recipient_messages if msg['id'] not in data['message_ids']]
    messages[recipient] = new_messages

    save_messages(messages)
    return jsonify({"status": f"Deleted {len(recipient_messages) - len(new_messages)} messages"}), 200


@app.route('/get_messages_range/<recipient>', methods=['GET'])
def get_messages_range(recipient):
    start = int(request.args.get('start', 0))
    stop = int(request.args.get('stop', 10))

    messages = load_messages()
    recipient_messages = messages.get(recipient, [])
    recipient_messages.sort(key=lambda x: x['timestamp'])

    return jsonify({"messages": recipient_messages[start:stop]}), 200


if __name__ == '__main__':
    app.run(debug=True)
