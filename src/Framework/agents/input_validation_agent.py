# File: /Framework/agents/input_validation_agent.py

from autogen import ConversableAgent
from .FDAWarningLetterValidator import FDAWarningLetterValidator
import os
import dspy

class InputValidationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="input_validation_agent",
            system_message="You validate FDA warning letters for correctness and completeness.",
            llm_config = {
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )

    def handle_message(self, messages, sender, **kwargs):
        # Access the warning letter from context
        warning_letter = self.context.get("warning_letter", "")
        # Implement validation logic here
        is_valid = self.validate_warning_letter(warning_letter)
        response_content = "Valid warning letter." if is_valid else "Invalid warning letter."
        return {"role": "assistant", "content": response_content}

    def validate_warning_letter(self, warning_letter):
        validator = FDAWarningLetterValidator()
        try:
            validator(warning_letter)
            return True  # Validation passed
        except dspy.DSPyError as e:
            print(f"Input validation failed: {e}")
            return False