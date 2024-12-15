# File: /Framework/agents/corrective_action_validation_agent.py

from autogen import ConversableAgent
import os
import json
import logging
from openai import OpenAI


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
        self.client = OpenAI(api_key=self.llm_config["api_key"])
        self.register_reply(
                trigger=self._always_true_trigger, # Add a specific trigger string
                reply_func=self.handle_message,
                position=0
            )
    def _always_true_trigger(self, sender):
        # This trigger function always returns True
        return True
    
    def handle_message(self, *args, **kwargs):
        #logging.debug(f"corrective_action_validation_agent: handle_message: messages={messages}, sender={sender}, kwargs={kwargs}")
        corrective_action_plan = self.context.get("corrective_action_plan", "")
        summary = self.context.get('summary', {})
        violated_terms = summary.get('violated_terms', [])
        template = self.context.get("template", "")
        
        # Prepare the validation prompt
        messages = [{
            "role": "user",
            "content": f"""
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
        }]
        max_retries = 5  # maximum number of retries
        retries = 0
        while retries < max_retries:
            response = self.client.chat.completions.create(
            model=self.llm_config["model"],
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        try:
            # Get the actual response content first
            response_content = response.choices[0].message.content.strip()
            # Then parse the content as JSON
            result = json.loads(response_content)
            self.context["corrective_action_validation"] = response_content
            return {"role": "assistant", "content": "Corrective action plan validated."}
        except json.JSONDecodeError:
            retries += 1