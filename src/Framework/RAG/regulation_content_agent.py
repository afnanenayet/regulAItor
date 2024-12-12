# File: Framework/RAG/regulation_content_agent.py

import json
import os

class RegulationContentAgent:
    def __init__(self):
        # Load the full regulations from the JSON file
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'full_regulations.json')
        with open(data_path, 'r') as f:
            self.regulations_data = json.load(f)

    def get_regulation_texts(self, regulations: list) -> dict:
        """
        Retrieves the full text of the provided regulation citations.

        :param regulations: A list of regulation citations.
        :return: A dictionary mapping regulation citations to their full texts.
        """
        regulation_texts = {}
        for reg in regulations:
            full_text = self.regulations_data.get(reg)
            if full_text:
                regulation_texts[reg] = full_text
            else:
                regulation_texts[reg] = "Full text not found for this regulation."
        return regulation_texts
