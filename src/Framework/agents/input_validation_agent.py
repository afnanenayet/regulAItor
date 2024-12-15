# File: /Framework/agents/input_validation_agent.py

from autogen import ConversableAgent
import os
import logging
import re
from dotenv import load_dotenv

load_dotenv()

class InputValidationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="input_validation_agent",
            system_message="You validate FDA warning letters for correctness and completeness.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )


        self.register_reply(
            trigger=self._always_true_trigger, # Add a specific trigger string
            reply_func=self.handle_message,
            position=0
        )
    def _always_true_trigger(self, sender):
        # This trigger function always returns True
        return True
    def handle_message(self, *args, **kwargs):
        # Access the warning letter from the context
        warning_letter = self.context.get("warning_letter", "")
        if not warning_letter:
            logging.error(f"{self.name}: No warning letter found in context.")
            self.context["input_validation_result"] = False
            response_content = "Validation failed. No warning letter provided."
            return {"role": "assistant", "content": response_content}

        # Perform validation on the warning letter
        is_valid, validation_feedback = self.validate_warning_letter(warning_letter)
        self.context["input_validation_result"] = is_valid
        if is_valid:
            response_content = "Validation successful."
        else:
            response_content = f"Validation failed. {validation_feedback}"

        return {"role": "assistant", "content": response_content}

    def validate_warning_letter(self, warning_letter):
        # Define key phrases that should be present in a valid FDA warning letter
        violation_phrases = [
            "violations of the FD&C Act",
            "violation of the Federal Food, Drug, and Cosmetic Act",
            "not in compliance with the FD&C Act",
            "FD&C Act compliance issues",
            "violative under the FD&C Act",
            "contrary to the FD&C Act",
        ]
        
        # Check for violation phrases
        if not any(phrase.lower() in warning_letter.lower() for phrase in violation_phrases):
            return False, "Missing key phrase indicating legal violations under the FD&C Act."
        
        # Check for FDA identification
        if not ("Food and Drug Administration" in warning_letter or "FDA" in warning_letter):
            return False, "Missing FDA identification."
        

        
        return True, ""