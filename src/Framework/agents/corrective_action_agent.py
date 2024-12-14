# File: /Framework/agents/corrective_action_agent.py

from autogen import ConversableAgent
import os
import logging

class CorrectiveActionAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="corrective_action_agent",
            system_message="""
You are a compliance assistant tasked with drafting a full corrective action plan to address all violated terms.
""",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
    
    def handle_message(self, messages, sender, **kwargs):
        #logging.debug(f"{self.name}: Received messages from {sender}: {messages}")
        violated_terms = self.context.get("violated_terms", [])
        recommendations = self.context.get("recommendations", "")
        regulation_texts = self.context.get("regulation_texts", {})
        template = self.context.get("template", "")
        
        # Prepare the prompt
        prompt = f"""
Using the following template, write a full corrective action plan addressing all violated terms.

Template:
{template}

Violated Terms:
{violated_terms}

Recommendations:
{recommendations}

Regulation Texts:
{regulation_texts}

Ensure that the corrective action plan addresses each violated term and follows the structure of the template.
"""
       # logging.debug(f"{self.name}: Prompt for LLM:\n{prompt}")

        corrective_action_plan = self.llm.generate(prompt)

      #  logging.debug(f"{self.name}: Generated corrective action plan:\n{corrective_action_plan.strip()}")

        self.context["corrective_action_plan"] = corrective_action_plan.strip()
        return {"role": "assistant", "content": "Corrective action plan drafted."}