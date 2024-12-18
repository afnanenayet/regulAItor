from autogen import ConversableAgent
import os
import logging
import re
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()


class InputValidationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="input_validation_agent",
            system_message="You validate FDA warning letters for correctness and completeness.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
        self.client = OpenAI(api_key=self.llm_config["api_key"])

        self.register_reply(
            trigger=self._always_true_trigger,  # Add a specific trigger string
            reply_func=self.handle_message,
            position=0,
        )

    def _always_true_trigger(self, sender):
        # This trigger function always returns True
        return True

    def handle_message(self, *args, **kwargs):
        # Access the warning letter from the context
        warning_letter = self.context.get("warning_letter", "")
        template = self.context.get("template", "")
        messages = [
            {
                "role": "user",
                "content": f"""
                Validate the following template for compliance with the required corrective action plan structure for responding to an FDA warning letter.

                Template to Validate:
                {template}

                Provide your feedback in JSON format with the following structure:

                If valid:
                {{
                "status": "Approved",
                "message": "Template matches required structure."
                }}
                If invalid:
                {{
                "status": "Rejected",
                "issues": ["List of missing or problematic sections"]
                }}
                """,
            }
        ]

        max_iterations = 5
        for i in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.llm_config["model"],
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )

            response = response.choices[0].message.content.strip()
            if isinstance(response, dict):
                response = response["content"]

            response = response.replace("```json", "").replace("```", "").strip()

            json_data = json.loads(response)
            is_valid = True
            if json_data.get("status") == "Approved":
                self.context["Valid_Template"] = True
                break

            elif json_data.get("status") == "Rejected" and i < max_iterations - 1:
                continue
            else:
                self.context["Valid_Template"] = False
                self.context["Valid_Template_feedback"] = json_data.get("issues")

        if not warning_letter:
            logging.error(f"{self.name}: No warning letter found in context.")
            self.context["input_validation_result"] = False
            response_content = "Validation failed. No warning letter provided."
            return {"role": "assistant", "content": response_content}

        # Perform validation on the warning letter
        is_valid, validation_feedback = self.validate_warning_letter(warning_letter)

        if is_valid is True:
            self.context["input_validation_result"] = is_valid
            response_content = "Validation successful."
        else:
            self.context["input_validation_result"] = False
            self.context["input_validation_result_feedback"] = validation_feedback
            response_content = f"Validation failed. {validation_feedback}"

        return {"role": "assistant", "content": response_content}

    def validate_warning_letter(self, warning_letter):
        # Define key phrases that should be present in a valid FDA warning letter
        violation_phrases = [
            "FD&C Act",
            "violation of the Federal Food, Drug, and Cosmetic Act",
            "ederal Food, Drug, and Cosmetic Act",
            "Food and Drug Administration",
        ]

        # Check for violation phrases
        if not any(
            phrase.lower() in warning_letter.lower() for phrase in violation_phrases
        ):
            return (
                False,
                "Missing key phrase indicating legal violations under the FD&C Act.",
            )

        return True, "Input warning letter is not Valid"
