from autogen import ConversableAgent
import json
import os
import logging
import re

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
        
        self.register_reply(
            trigger=self._always_true_trigger, 
            reply_func=self.full_regulation_search,
            position=0
        )

    def _always_true_trigger(self, sender):
        return True

    def full_regulation_search(self, *args, **kwargs):
        summary = self.context.get('summary', {})
        violated_terms = summary.get('violated_terms', [])
        
        regulations = self.extract_regulation_numbers(violated_terms)
        regulation_texts = self.get_regulation_texts(regulations)
        
        self.context["regulation_full_texts"] = regulation_texts
        
        return True, {"role": "assistant", "content": "Regulation texts provided."}

    def extract_regulation_numbers(self, violated_terms):
        import re
        regulation_numbers = []
        for term in violated_terms:
            matches = re.findall(r'section \d+ of the FD&C Act \[21 U.S.C. § \d+(?:\.\d+)?\]', term)
            for match in matches:
                section_match = re.search(r'section (\d+)', match)
                if section_match:
                    section_number = section_match.group(1)
                    regulation_number = f"21 U.S.C. § {section_number}"
                    regulation_numbers.append(regulation_number)
                usc_match = re.search(r'\[21 U.S.C. § (\d+(?:\.\d+)?)\]', match)
                if usc_match:
                    usc_section_number = usc_match.group(1)
                    regulation_numbers.append(f"21 U.S.C. § {usc_section_number}")
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