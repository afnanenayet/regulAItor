from autogen import ConversableAgent
import json
import asyncio
from typing import Dict, Optional
import logging
import re
from config import ProcessorConfig, AgentConfig
from rate_limiter import RateLimiter


class FDALetterProcessor:
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.agent_config = AgentConfig()
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)

        self.extractor_agent = ConversableAgent(
            name="Extractor",
            system_message="""
                {
                "role": "FDA Regulatory Compliance Extractor",
                "task": "Extract violated terms and recommendations from FDA warning letters.",
                "input_format": "FDA warning letter text",
                "output_format": {
                    "violated_terms": ["array of violated terms"],
                    "recommendations": ["array of recommendations"]
                },
                "instructions": [
                    "1. Extract violated terms:",
                    "   - Identify specific violations referenced in the warning letter.",
                    "   - Return the terms only, without additional details or citations.",
                    "",
                    "2. Extract FDA recommendations:",
                    "   - Identify the recommendations provided in the warning letter.",
                    "   - Return the recommendations only, without further descriptions or actions."
                ],
                "output_rules": [
                    "Return results in JSON format only.",
                    "List violated terms and recommendations"
                ]
                }
            """,
            llm_config=self.agent_config.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

        # Initialize the Validator agent with improved termination logic
        def validator_is_termination_msg(message):
            if isinstance(message, dict) and "content" in message:
                content = message["content"].lower()
                return "approved" in content
            return False

        self.validator_agent = ConversableAgent(
            name="Validator",
            system_message="""
            {
                "role": "FDA Compliance Validation Agent",
                "task": "Validate extracted violations and recommendations against original warning letter",
                "validation_criteria": {
                    "1. Violation Context Validation": [
                        "Verify complete violation descriptions are captured",
                        "Confirm both context and citations are accurate",
                        "Check for proper reference to relevant Acts/sections",
                        "Ensure violation descriptions match the original letter"
                    ],
                    "2. Recommendation Validation": [
                        "Verify recommendations address specific manufacturing contexts",
                        "Ensure recommendations match violation contexts",
                        "Confirm technical accuracy of corrective actions",
                        "Check for manufacturing-specific details"
                    ],
                    "3. Completeness Validation": [
                        "Verify all contextual information is preserved",
                        "Confirm no critical details are omitted",
                        "Check for proper connection between violations and recommendations"
                    ]
                },
                "output_format": {
                    "if_approved": {
                        "status": "APPROVED",
                        "feedback": "Validation notes on context and completeness"
                    },
                    "if_rejected": {
                        "status": "REJECTED",
                        "feedback": "Detailed explanation of missing context or inaccuracies",
                        "revised_summary": {
                            "violated_terms": ["full violation descriptions with citations"],
                            "recommendations": ["detailed corrective actions"]
                        }
                    }
                }
            }
            """,
            llm_config=self.agent_config.llm_config,
            human_input_mode="NEVER",
            is_termination_msg=validator_is_termination_msg,
            max_consecutive_auto_reply=3,
        )

    async def process_letter(self, letter_name: str, content: str) -> Optional[Dict]:
        """
        Processes the FDA warning letter asynchronously.
        """
        try:
            # Initial message to the Extractor agent
            initial_message = {
                "content": content,
                "role": "user",  # Assuming the role is 'user' when initiating the conversation
            }

            # Start the conversation between Extractor and Validator
            chat_result = await self.extractor_agent.a_initiate_chat(
                self.validator_agent,
                message=initial_message,
                max_turns=self.config.max_turns,
            )

            # Retrieve the final response from the Extractor
            extraction_response = None
            for message in reversed(chat_result.chat_history):
                # Debug: Print message to inspect its structure
                print(f"Message: {message}")

                # Use 'name' instead of 'sender'
                if (
                    message.get("name") == "Extractor"
                    and message.get("role") == "assistant"
                ):
                    extraction_response = message["content"]
                    break
            else:
                logging.error("No extraction response found from Extractor.")
                return None

            if not extraction_response:
                logging.error("Extraction response is empty.")
                return None

            # Parse the extraction response
            extraction_result = self.parse_json_response(
                extraction_response, letter_name, "extraction"
            )
            if not extraction_result:
                logging.error("Failed to parse extraction response.")
                return None

            # Return the final result
            return {
                "letter_name": letter_name,
                "violated_terms": extraction_result.get("violated_terms", []),
                "recommendations": extraction_result.get("recommendations", []),
            }

        except Exception as e:
            logging.error(f"Error processing letter {letter_name}: {e}")
            return None

    def parse_json_response(
        self, response_content: str, letter_name: str, stage: str
    ) -> Optional[Dict]:
        """
        Parses the JSON response content.
        """
        try:
            content = response_content.strip()
            # Remove any code block markers
            content = re.sub(r"^```json", "", content)
            content = re.sub(r"```$", "", content)
            return json.loads(content)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error during {stage} for {letter_name}: {e}")
            return None
