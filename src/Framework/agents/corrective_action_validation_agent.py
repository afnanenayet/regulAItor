# File: /Framework/agents/corrective_action_validation_agent.py

from autogen import ConversableAgent
import os
import json
import logging

class CorrectiveActionValidationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="corrective_action_validation_agent",
            system_message="""
You validate corrective action plans for compliance, accuracy, and completeness.
""",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
    
    def handle_message(self, messages, sender, **kwargs):
        #logging.debug(f"corrective_action_validation_agent: handle_message: messages={messages}, sender={sender}, kwargs={kwargs}")
        corrective_action_plan = self.context.get("corrective_action_plan", "")
        violated_terms = self.context.get("violated_terms", [])
        template = self.context.get("template", "")
        
        # Prepare the validation prompt
        prompt = f"""
Validate the following corrective action plan for compliance, accuracy, and completeness.

Corrective Action Plan:
{corrective_action_plan}

Violated Terms:
{violated_terms}

Template:
{template}

Provide your feedback in JSON format with the following structure:

If approved:
{{
  "status": "APPROVED",
  "feedback": "Validation notes."
}}
If changes are needed:
{{
  "status": "CHANGES_REQUIRED",
  "feedback": "Detailed feedback on required changes."
}}
"""
        response = self.llm.generate(prompt)
        try:
            result = json.loads(response)
            self.context["corrective_action_validation"] = result
            return {"role": "assistant", "content": "Corrective action plan validated."}
        except json.JSONDecodeError:
            self.context["corrective_action_validation"] = {"status": "CHANGES_REQUIRED", "feedback": "Invalid JSON response."}
            return {
                "role": "assistant",
                "content": "Validation failed. Response could not be parsed."
            }