# File: /Framework/main.py

from flask import Flask, request, jsonify
from agents.agent_manager import agent_manager
from agents.conversation_workflow import conversation_workflow

app = Flask(__name__)

@app.route('/process_warning_letter', methods=['POST'])
def process_warning_letter():
    data = request.get_json()
    warning_letter = data.get('warning_letter', '')
    template = data.get('template', '')

    # Set context for all agents
    for agent in agent_manager.groupchat.agents:
        agent.context = {"warning_letter": warning_letter, "template": template}

    # Run the conversation workflow
    conversation_workflow(agent_manager)

    # Collect results from the corrective action agent
    corrective_action_plan = agent_manager.groupchat.agents[-2].context.get("corrective_action_plan", "")
    return jsonify({"corrective_action_plan": corrective_action_plan})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)