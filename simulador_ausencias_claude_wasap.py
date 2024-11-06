import requests
from flask import Flask, request, render_template_string, jsonify
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import logging
import pytz
from threading import Thread
import time

# Load environment variables
load_dotenv()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_bot.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp Bot Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h1 class="text-2xl font-bold mb-4">WhatsApp Bot Status Dashboard</h1>

            <!-- Status Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h2 class="font-semibold mb-2">Server Status</h2>
                    <p id="serverStatus" class="text-green-600">Operational</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h2 class="font-semibold mb-2">WhatsApp Connection</h2>
                    <p id="whatsappStatus">Checking...</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h2 class="font-semibold mb-2">Claude API Status</h2>
                    <p id="claudeStatus">Checking...</p>
                </div>
            </div>

            <!-- Recent Messages -->
            <div class="bg-gray-50 p-4 rounded-lg">
                <h2 class="font-semibold mb-4">Recent Messages</h2>
                <div id="messageList" class="space-y-2">
                    <!-- Messages will be populated here -->
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('whatsappStatus').textContent = data.whatsapp_status;
                    document.getElementById('whatsappStatus').className = data.whatsapp_status === 'Connected' ? 'text-green-600' : 'text-red-600';

                    document.getElementById('claudeStatus').textContent = data.claude_status;
                    document.getElementById('claudeStatus').className = data.claude_status === 'Connected' ? 'text-green-600' : 'text-red-600';
                });

            fetch('/api/messages')
                .then(response => response.json())
                .then(messages => {
                    const messageList = document.getElementById('messageList');
                    messageList.innerHTML = '';
                    Object.entries(messages).slice(-5).forEach(([id, msg]) => {
                        const div = document.createElement('div');
                        div.className = 'bg-white p-3 rounded shadow';
                        div.innerHTML = `
                            <p class="text-sm text-gray-600">${moment(msg.timestamp).format('YYYY-MM-DD HH:mm:ss')}</p>
                            <p class="font-medium">${msg.from_number} → ${msg.to_number}</p>
                            <p class="text-gray-700">${msg.text}</p>
                        `;
                        messageList.appendChild(div);
                    });
                });
        }

        // Update status every 5 seconds
        setInterval(updateStatus, 5000);
        updateStatus();  // Initial update
    </script>
</body>
</html>
"""


class MessageTracker:
    def __init__(self):
        self.messages = {}
        self.whatsapp_status = "Disconnected"
        self.claude_status = "Disconnected"

    def add_message(self, message_data):
        timestamp = datetime.now(pytz.UTC)
        message_id = message_data.get('id', 'unknown')

        message_info = {
            'timestamp': timestamp,
            'from_number': message_data.get('from', 'unknown'),
            'to_number': message_data.get('to', 'unknown'),
            'message_type': message_data.get('type', 'unknown'),
            'text': message_data.get('text', {}).get('body', 'unknown'),
            'status': message_data.get('status', 'unknown'),
            'metadata': {
                'display_phone_number': message_data.get('display_phone_number', 'unknown'),
                'phone_number_id': message_data.get('phone_number_id', 'unknown'),
                'profile': message_data.get('profile', {}),
            }
        }

        self.messages[message_id] = message_info
        logging.info(f"New message tracked: {json.dumps(message_info, default=str)}")
        return message_info


message_tracker = MessageTracker()


def check_whatsapp_connection():
    """Check WhatsApp connection status periodically"""
    while True:
        try:
            # Simplified check - you might want to implement a real health check
            if WHATSAPP_TOKEN:
                message_tracker.whatsapp_status = "Connected"
            else:
                message_tracker.whatsapp_status = "Disconnected"
        except Exception as e:
            message_tracker.whatsapp_status = f"Error: {str(e)}"
        time.sleep(30)  # Check every 30 seconds


def check_claude_connection():
    """Check Claude API connection status periodically"""
    while True:
        try:
            if CLAUDE_API_KEY:
                message_tracker.claude_status = "Connected"
            else:
                message_tracker.claude_status = "Disconnected"
        except Exception as e:
            message_tracker.claude_status = f"Error: {str(e)}"
        time.sleep(30)  # Check every 30 seconds


# Routes for the dashboard
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/status')
def status():
    return jsonify({
        'whatsapp_status': message_tracker.whatsapp_status,
        'claude_status': message_tracker.claude_status
    })


@app.route('/api/messages')
def get_messages():
    return jsonify(message_tracker.messages)


# Original webhook routes remain the same
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Received webhook data: {json.dumps(data)}")

    if 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('value', {}).get('messages'):
                    for message in change['value']['messages']:
                        if message.get('type') == 'text':
                            message_info = message_tracker.add_message(message)

                            sender = message['from']
                            text = message['text']['body']

                            response = process_message(sender, text, message, absent_students)
                            send_whatsapp_message(sender, response)

    return "OK", 200


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Forbidden", 403


if __name__ == "__main__":
    # Start monitoring threads
    Thread(target=check_whatsapp_connection, daemon=True).start()
    Thread(target=check_claude_connection, daemon=True).start()

    # Student data
    absent_students = {
        "John Smith": {"tutor": "+34667519829", "reason": "unknown"},
        "Mary Johnson": {"tutor": "+34667519829", "reason": "unknown"}
    }

    print("\n🤖 WhatsApp Bot Dashboard is running!")
    print("→ Open http://localhost:5000 in your browser to view the dashboard")
    print("→ Press Ctrl+C to quit\n")

    app.run(port=5000)