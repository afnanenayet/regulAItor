# File: /Framework/agents/regulation_content_agent.py

from autogen import ConversableAgent
import json
import os
import logging

class RegulationContentAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="regulation_content_agent",
            system_message="You provide the full text of specific regulations based on their citations.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'full_regulations.json')
        try:
            with open(data_path, 'r') as f:
                self.regulations_data = json.load(f)
        except FileNotFoundError:
            self.regulations_data = {}
            print(f"Warning: 'full_regulations.json' not found at {data_path}.")
                # Register the retrieval function with a specific trigger
        self.register_reply(
            trigger=self._always_true_trigger, # Add a specific trigger string
            reply_func=self.handle_message,
            position=0
        )
    def _always_true_trigger(self, sender):
        # This trigger function always returns True
        return True

    def handle_message(self, messages=None, sender=None, **kwargs):
      #  logging.debug(f"Received message: {messages}")
        summary = self.context.get('summary', {})
        violated_terms = summary.get('violated_terms', [])       
        regulations = self.extract_regulation_numbers(violated_terms)
        regulation_texts = self.get_regulation_texts(regulations)
        self.context["regulation_texts"] = regulation_texts
        return {"role": "assistant", "content": "Regulation texts provided."}

    def extract_regulation_numbers(self, violated_terms):
        import re
        regulation_numbers = []
        for term in violated_terms:
            matches = re.findall(r'\b\d+\sCFR\s\d+(?:\.\d+)?', term)
            regulation_numbers.extend(matches)
        return list(set(regulation_numbers))

    def get_regulation_texts(self, regulations):
        regulation_texts = {}
        for reg in regulations:
            full_text = self.regulations_data.get(reg)
            if full_text:
                regulation_texts[reg] = full_text
            else:
                regulation_texts[reg] = "Full text not found for this regulation."
        return regulation_texts