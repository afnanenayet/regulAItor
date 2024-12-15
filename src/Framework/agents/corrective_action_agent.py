# File: /Framework/agents/corrective_action_agent.py

from autogen import ConversableAgent
import os
import logging
from openai import OpenAI


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
        #logging.debug(f"{self.name}: Received messages from {sender}: {messages}")
        warning_letter = self.context.get("warning_letter", "")
        summary = self.context.get('summary', {})
        violated_terms = summary.get('violated_terms', [])
        recommendations = self.context.get("recommendations", "")
        regulation_texts = self.context.get("regulation_full_texts", {})
        template = self.context.get("template", "")
        
        # Prepare the prompt
        messages = [{
            "role": "user",
            "content": f"""
        Using the following template, create a comprehensive corrective action plan that addresses all violated terms.  

        **Template:**  
        {template}  

        **Warning Letter**
        {warning_letter}

        **Violated Terms:**  
        {violated_terms}  

        **Recommendations:**  
        {recommendations}  

        **Regulation Context:**  
        {regulation_texts}  

        Ensure the corrective action plan incorporates the recommendations and aligns thoroughly with the full regulatory context, addressing each violated term systematically.
        """
        }]
       # logging.debug(f"{self.name}: Prompt for LLM:\n{prompt}")

        response = self.client.chat.completions.create(
            model=self.llm_config["model"],
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
      #  logging.debug(f"{self.name}: Generated corrective action plan:\n{corrective_action_plan.strip()}")

        self.context["corrective_action_plan"] = response.choices[0].message.content.strip()
        return {"role": "assistant", "content": "Corrective action plan drafted."}