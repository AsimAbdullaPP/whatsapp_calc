import re
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.urls import unquote  # Updated import

app = Flask(__name__)

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

# Home route
@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Calc API is running!"

# Command handling route
@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    command = data.get("command", "")
    messages = data.get("messages", [])
    result = handle_settle_command(command, messages)
    return jsonify({"result": result})

def parse_command(command):
    """Extract operation and optional start marker."""
    pattern = r'^/settle_(\w+)(?:\s+-start\s+\'"[\'"])?$'
    match = re.match(pattern, command.strip())
    if match:
        return match.group(1), match.group(2)  # (operation, start_marker)
    return None, None

def extract_numbers(messages):
    """Extract all numbers from a list of message strings."""
    numbers = []
    for msg in messages:
        numbers += list(map(float, re.findall(r'\d+\.?\d*', msg)))
    return numbers

def calculate_result(numbers, operation):
    if not numbers:
        return "No numbers found."
    if operation == 'a':
        result = sum(numbers)
        expr = ' + '.join(map(str, numbers))
    elif operation == 's':
        result = numbers[0] - sum(numbers[1:]) if len(numbers) > 1 else numbers[0]
        expr = ' - '.join(map(str, numbers))
    elif operation == 'm':
        result = 1
        for n in numbers:
            result *= n
        expr = ' * '.join(map(str, numbers))
    elif operation == 'd':
        result = numbers[0]
        for n in numbers[1:]:
            if n == 0:
                return "Division by zero error."
            result /= n
        expr = ' / '.join(map(str, numbers))
    else:
        return "Invalid operation."
    return f"{expr} = {result}"

def handle_settle_command(command, all_messages):
    operation, start_marker = parse_command(command)
    if not operation:
        return "Invalid command format."
    start_index = 0
    if start_marker:
        for i, msg in enumerate(all_messages):
            if start_marker in msg:
                start_index = i + 1
                break
    selected_messages = all_messages[start_index:]
    numbers = extract_numbers(selected_messages)
    return calculate_result(numbers, operation)

# WhatsApp reply route
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "").strip()
    # Simulated past messages list (you'll automate this later)
    messages = [
        "start", "100", "250", "another message", "300", "12", "34"
    ]
    result = handle_settle_command(incoming_msg, messages)
    resp = MessagingResponse()
    resp.message(result)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
