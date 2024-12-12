# File: Framework/agents/regulation_extraction_agent.py

from autogen import AssistantAgent

class RegulationExtractionAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="regulation_extraction_agent",
            system_message="You extract specific violated regulations from FDA warning letters.",
            llm_config={
                "model": "gpt-4",
                "api_key": "YOUR_OPENAI_API_KEY",
            },
        )

    def handle_message(self, message):
        warning_letter = message.get("warning_letter", "")
        regulations = self.extract_regulations(warning_letter)
        return {"regulations": regulations}

    def extract_regulations(self, warning_letter):
        # Use the LLM to extract regulations
        prompt = f"Extract all specific regulation citations (e.g., '21 CFR 211.22') from the following FDA warning letter:\n\n{warning_letter}"
        response = self.llm.generate(prompt)
        # Process the response into a list
        regulations = [line.strip() for line in response.split('\n') if line.strip()]
        return regulations