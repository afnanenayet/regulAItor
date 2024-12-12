# File: Framework/main.py

from flask import Flask, request, jsonify
from agents.agent_manager import agent_manager
from agents.conversation_workflow import conversation_workflow

app = Flask(__name__)

@app.route('/process_warning_letter', methods=['POST'])
def process_warning_letter():
    data = request.get_json()
    warning_letter = data.get('warning_letter', '')

    # Set the warning letter in the agent manager context
    agent_manager.set_context({"warning_letter": warning_letter})

    # Run the conversation workflow
    result = conversation_workflow(agent_manager)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)