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
        
        # Pattern to match citations like "21 CFR 211.208" or "21 U.S.C. 331"
        pattern = r'(21)\s+(CFR|C\.F\.R\.|USC|U\.S\.C\.)\s+(\d+(?:\.\d+)*)'

        for term in violated_terms:
            term_str = str(term)
            matches = re.finditer(pattern, term_str, re.IGNORECASE)
            
            for match in matches:
                # Extract parts of the citation
                title = match.group(1)
                cfr_or_usc = match.group(2).upper().replace('.', '')  # Normalize to "CFR" or "USC"
                section_number = match.group(3)
                
                # Construct the regulation key
                regulation_key = f"{title} {cfr_or_usc} {section_number}"
                
                # Avoid duplicates
                if regulation_key not in regulation_numbers:
                    regulation_numbers.append(regulation_key)
                    
        return regulation_numbers

    def get_regulation_texts(self, regulations):
        regulation_texts = {}
        for reg in regulations:
            full_text = self.regulations_data.get(reg)
            if full_text:
                regulation_texts[reg] = full_text
            else:
                regulation_texts[reg] = "Full text not found for this regulation."
        return regulation_texts