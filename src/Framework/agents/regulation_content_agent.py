# File: Framework/agents/regulation_content_agent.py

from autogen import AssistantAgent
import json
import os

class RegulationContentAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="regulation_content_agent",
            system_message="You provide the full text of specific regulations based on their citations.",
            llm_config={
                "model": "gpt-4",
                "api_key": "YOUR_OPENAI_API_KEY",
            },
        )
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'full_regulations.json')
        with open(data_path, 'r') as f:
            self.regulations_data = json.load(f)

    def handle_message(self, message):
        regulations = message.get("regulations", [])
        regulation_texts = self.get_regulation_texts(regulations)
        return {"regulation_texts": regulation_texts}

    def get_regulation_texts(self, regulations):
        regulation_texts = {}
        for reg in regulations:
            full_text = self.regulations_data.get(reg)
            if full_text:
                regulation_texts[reg] = full_text
            else:
                regulation_texts[reg] = "Full text not found for this regulation."
        return regulation_texts